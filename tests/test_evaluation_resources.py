"""The opt-in evaluator stops during active work when resource sampling fails."""

from __future__ import annotations

import importlib
import json
import threading
import time
from pathlib import Path

import pytest


@pytest.fixture
def resources(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    return importlib.import_module("model_evaluation04.resources")


def report(output):
    return json.loads((output / "resource-monitor.json").read_text("utf-8"))


def test_low_ram_interrupts_active_stream_without_waiting_for_completion(tmp_path, resources):
    pressure = threading.Event()
    sampled_pressure = threading.Event()

    def sampler():
        available = 2_000_000_000 if pressure.is_set() else 8_000_000_000
        if pressure.is_set():
            sampled_pressure.set()
        return resources.ResourceSample(available, 1234, (789,))

    monitor = resources.ResourceMonitor(tmp_path, sampler=sampler, interval=0.005)
    with pytest.raises(resources.EvaluationStop, match="Available RAM"):
        with monitor:
            pressure.set()
            # This is a streaming transport waiting for its next network chunk.
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                monitor.check()
                time.sleep(0.002)
            pytest.fail("The guard waited for stream completion instead of interrupting")
    assert sampled_pressure.is_set()
    evidence = report(tmp_path)
    assert evidence["minimum_sampled_ram_bytes"] == 2_000_000_000
    assert evidence["samples"][-1]["owned_rss_bytes"] == 1234
    assert evidence["failure"] and evidence["shutdown"] == "stopped"
    assert not monitor.running


def test_sampler_exception_fails_closed_and_stops_thread(tmp_path, resources):
    fail = threading.Event()

    def sampler():
        if fail.is_set():
            raise OSError("RAM counter unavailable")
        return resources.ResourceSample(8_000_000_000)

    monitor = resources.ResourceMonitor(tmp_path, sampler=sampler, interval=0.005)
    with pytest.raises(resources.EvaluationStop, match="RAM counter unavailable"):
        with monitor:
            fail.set()
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                monitor.check()
                time.sleep(0.002)
            pytest.fail("A broken sampler was ignored")
    assert "RAM counter unavailable" in report(tmp_path)["failure"]
    assert not monitor.running


def test_normal_context_exit_wakes_monitor_and_preserves_minimum(tmp_path, resources):
    monitor = resources.ResourceMonitor(
        tmp_path, sampler=lambda: resources.ResourceSample(8_000_000_000), interval=60
    )
    with monitor:
        monitor.check()
        assert monitor.running
    assert not monitor.running
    evidence = report(tmp_path)
    assert evidence["minimum_sampled_ram_bytes"] == 8_000_000_000
    assert evidence["failure"] is None
    assert evidence["shutdown"] == "stopped"


def test_blocked_sampler_reports_bounded_shutdown_timeout(tmp_path, resources):
    block = threading.Event()
    entered = threading.Event()
    release = threading.Event()

    def sampler():
        if block.is_set():
            entered.set()
            release.wait(2)
        return resources.ResourceSample(8_000_000_000)

    monitor = resources.ResourceMonitor(tmp_path, sampler=sampler, interval=0.005, join_timeout=0.03)
    try:
        with pytest.raises(resources.EvaluationStop, match="shutdown timed out"):
            with monitor:
                block.set()
                assert entered.wait(1)
        evidence = report(tmp_path)
        assert evidence["shutdown"] == "timed_out"
        assert "shutdown timed out" in evidence["failure"]
    finally:
        release.set()
        deadline = time.monotonic() + 2
        while monitor.running and time.monotonic() < deadline:
            time.sleep(0.005)
    assert not monitor.running


def test_initial_low_ram_prevents_context_body(tmp_path, resources):
    monitor = resources.ResourceMonitor(
        tmp_path, sampler=lambda: resources.ResourceSample(1_000_000_000), interval=0.005
    )
    with pytest.raises(resources.EvaluationStop, match="Available RAM"):
        with monitor:
            pytest.fail("Unsafe initial resources reached evaluation")
    assert not monitor.running
    assert report(tmp_path)["shutdown"] == "stopped"


def test_initial_sampler_exception_prevents_context_body(tmp_path, resources):
    def sampler():
        raise resources.psutil.AccessDenied(456)

    monitor = resources.ResourceMonitor(tmp_path, sampler=sampler)
    with pytest.raises(resources.EvaluationStop, match="AccessDenied"):
        with monitor:
            pytest.fail("Missing resource access reached evaluation")
    assert not monitor.running
    assert "AccessDenied" in report(tmp_path)["failure"]


def test_initial_sampler_hang_has_bounded_failure(tmp_path, resources):
    release = threading.Event()

    def sampler():
        release.wait(2)
        return resources.ResourceSample(8_000_000_000)

    monitor = resources.ResourceMonitor(tmp_path, sampler=sampler, join_timeout=0.02)
    try:
        with pytest.raises(resources.EvaluationStop, match="shutdown timed out"):
            with monitor:
                pytest.fail("Unmeasured resources reached evaluation")
        evidence = report(tmp_path)
        assert evidence["shutdown"] == "timed_out"
        assert evidence["minimum_sampled_ram_bytes"] is None
        assert "initial measurement" in evidence["failure"]
    finally:
        release.set()
        deadline = time.monotonic() + 2
        while monitor.running and time.monotonic() < deadline:
            time.sleep(0.005)
    assert not monitor.running


def test_unwritable_evidence_fails_closed(tmp_path, resources, monkeypatch):
    def unwritable(*args, **kwargs):
        raise OSError("Evidence drive unavailable")

    monkeypatch.setattr(resources, "write_json", unwritable)
    monitor = resources.ResourceMonitor(tmp_path, sampler=lambda: resources.ResourceSample(8_000_000_000))
    with pytest.raises(resources.EvaluationStop, match="Evidence drive unavailable"):
        with monitor:
            pytest.fail("Evaluation continued without writable evidence")
    assert not monitor.running


def test_default_sampler_counts_owned_tree_once_and_ignores_exited_children(resources, monkeypatch):
    class Process:
        def __init__(self, pid, rss, children=()):
            self.pid, self.rss, self.descendants = pid, rss, children

        def is_running(self):
            return True

        def children(self, recursive):
            assert recursive
            return self.descendants

        def memory_info(self):
            if self.rss is None:
                raise resources.psutil.NoSuchProcess(self.pid)
            return type("Memory", (), {"rss": self.rss})()

    child = Process(11, 200)
    parent = Process(10, 100, (child, Process(12, None)))
    monkeypatch.setattr(resources.psutil, "virtual_memory", lambda: type("Memory", (), {"available": 9000})())
    sample = resources.sample_resources((parent, child))
    assert sample == resources.ResourceSample(9000, 300, (10, 11))
