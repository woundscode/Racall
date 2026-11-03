"""The isolated evaluator must not compete with a user's active Ollama server."""

from __future__ import annotations

import importlib
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest


@pytest.fixture
def module(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    return importlib.import_module("model_evaluation04.guard")


def make_guard(module, tmp_path, **overrides):
    return module.MonitoredGuard(
        tmp_path,
        "http://127.0.0.1:11435/v1",
        "owned-test",
        "source",
        **{"monitor": SimpleNamespace(check=lambda: None), **overrides},
    )


def fake_observer(monkeypatch, payload=None, error=None):
    requests = []

    class Client:
        def __init__(self, **kwargs):
            assert kwargs == {"timeout": 5, "trust_env": False}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, url):
            requests.append(url)
            if error:
                raise error
            return SimpleNamespace(raise_for_status=lambda: SimpleNamespace(json=lambda: payload))

    monkeypatch.setattr(httpx, "Client", Client)
    return requests


def base_runtime(monkeypatch, module):
    calls = []

    def runtime(self, label):
        calls.append(label)
        return "delegated"

    monkeypatch.setattr(module.LiveGuard, "runtime", runtime)
    return calls


def test_monitor_failure_stops_before_observer_and_runtime(tmp_path, module, monkeypatch):
    def failed():
        raise module.EvaluationStop("RAM below safe floor")

    observer = fake_observer(monkeypatch, {"models": []})
    calls = base_runtime(monkeypatch, module)
    guard = make_guard(
        module, tmp_path, monitor=SimpleNamespace(check=failed), observe_endpoint="http://localhost:11434/v1"
    )
    with pytest.raises(module.EvaluationStop, match="RAM below safe floor"):
        guard.runtime("before model")
    assert calls == observer == []


@pytest.mark.parametrize(
    "endpoint", ["https://example.com/v1", "http://192.168.1.10:11434/v1", "http://127.0.0.1:11435/v1"]
)
def test_observer_rejects_remote_or_identical_server(tmp_path, module, endpoint):
    with pytest.raises(ValueError):
        make_guard(module, tmp_path, observe_endpoint=endpoint)


def test_loopback_spelling_does_not_bypass_same_server_check(tmp_path, module):
    with pytest.raises(ValueError, match="differ"):
        make_guard(module, tmp_path, observe_endpoint="http://localhost:11435/v1")


@pytest.mark.parametrize("models", [[{"name": "user-active-model"}], None, {}])
def test_active_or_unreadable_observer_stops_before_model(tmp_path, module, monkeypatch, models):
    requests = fake_observer(monkeypatch, {"models": models})
    calls = base_runtime(monkeypatch, module)
    guard = make_guard(module, tmp_path, observe_endpoint="http://127.0.0.1:11434/v1")
    with pytest.raises(module.EvaluationStop, match="User Ollama observation failed"):
        guard.runtime("before model")
    assert requests == ["http://127.0.0.1:11434/api/ps"]
    assert calls == []
    assert guard.failure


def test_unreachable_observer_stops_before_model(tmp_path, module, monkeypatch):
    fake_observer(monkeypatch, error=httpx.ConnectError("Observer unreachable"))
    calls = base_runtime(monkeypatch, module)
    guard = make_guard(module, tmp_path, observe_endpoint="http://127.0.0.1:11434/v1")
    with pytest.raises(module.EvaluationStop, match="Observer unreachable"):
        guard.runtime("before model")
    assert calls == []


def test_idle_observer_delegates_existing_runtime_checks(tmp_path, module, monkeypatch):
    requests = fake_observer(monkeypatch, {"models": []})
    calls = base_runtime(monkeypatch, module)
    guard = make_guard(module, tmp_path, observe_endpoint="http://127.0.0.1:11434/v1")
    assert guard.runtime("before model") == "delegated"
    assert requests == ["http://127.0.0.1:11434/api/ps"]
    assert calls == ["before model"]
