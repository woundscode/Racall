"""Continuous, read-only RAM monitoring for an explicitly owned evaluation run."""

from __future__ import annotations

import math
import threading
from collections import deque
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

import psutil
from model_evaluation03.guard import EvaluationStop, timestamp, write_json


@dataclass(frozen=True)
class ResourceSample:
    available_ram_bytes: int
    owned_rss_bytes: int = 0
    owned_pids: tuple[int, ...] = ()

    def __post_init__(self):
        for value in (self.available_ram_bytes, self.owned_rss_bytes):
            if type(value) is not int or value < 0:
                raise ValueError("RAM/RSS measurements must be nonnegative integer bytes")


def _owned_tree(roots):
    """Process objects retain identity; a recycled root PID is not followed."""
    processes = {}
    for root in roots:
        try:
            if root.is_running():
                for process in (root, *root.children(recursive=True)):
                    processes[process.pid] = process
        except psutil.NoSuchProcess:
            continue
    return processes.values()


def sample_resources(owned_processes=()) -> ResourceSample:
    available = psutil.virtual_memory().available
    resident = {}
    for process in _owned_tree(owned_processes):
        try:
            resident[process.pid] = process.memory_info().rss
        except psutil.NoSuchProcess:
            continue
    return ResourceSample(available, sum(resident.values()), tuple(sorted(resident)))


class ResourceMonitor:
    """Call check() from the active stream's cancellation checkpoint.

    No models or processes are started/stopped here. RSS is the sum for the owned
    tree, so shared pages can be counted more than once. The RAM guard uses the
    operating system's available memory, not that diagnostic RSS sum.
    """

    def __init__(
        self,
        output: Path,
        owned_pids: Iterable[int] = (),
        minimum_ram_bytes: int = 2_500_000_000,
        interval: float = 1.0,
        *,
        sampler: Callable[[], ResourceSample] | None = None,
        join_timeout: float = 3.0,
    ):
        if minimum_ram_bytes <= 0:
            raise ValueError("The available-RAM floor must be positive")
        if any(not math.isfinite(value) or value <= 0 for value in (interval, join_timeout)):
            raise ValueError("Sampling and shutdown intervals must be finite and positive")
        self.output = Path(output)
        self.minimum_ram_bytes = minimum_ram_bytes
        self.interval, self.join_timeout = interval, join_timeout
        self._pids = tuple(owned_pids)
        self._roots = None
        self._sampler = sampler or self._default_sample
        self._stop, self._ready = threading.Event(), threading.Event()
        self._lock = threading.RLock()
        self._thread = None
        self._samples = deque(maxlen=3600)
        self._sample_count = 0
        self._minimum = None
        self.failure = None
        self._shutdown = "not_started"

    def _default_sample(self):
        if self._roots is None:
            self._roots = tuple(psutil.Process(pid) for pid in self._pids)
        return sample_resources(self._roots)

    @property
    def running(self):
        return self._thread is not None and self._thread.is_alive()

    def check(self):
        if self.failure is not None:
            raise EvaluationStop(self.failure)

    def _save(self):
        write_json(
            self.output / "resource-monitor.json",
            {
                "minimum_ram_bytes": self.minimum_ram_bytes,
                "interval_seconds": self.interval,
                "owned_root_pids": self._pids,
                "sample_count": self._sample_count,
                "retained_sample_limit": self._samples.maxlen,
                "minimum_sampled_ram_bytes": self._minimum,
                "samples": list(self._samples),
                "failure": self.failure,
                "shutdown": self._shutdown,
            },
        )

    def _fail(self, message):
        with self._lock:
            self.failure = self.failure or message
            try:
                self._save()
            except OSError as error:
                self.failure += f"; unable to persist resource evidence: {error}"

    def _record(self, sample):
        if not isinstance(sample, ResourceSample):
            raise TypeError("Sampler must return ResourceSample")
        with self._lock:
            self._sample_count += 1
            self._samples.append({"at": timestamp(), **asdict(sample)})
            self._minimum = (
                sample.available_ram_bytes
                if self._minimum is None
                else min(self._minimum, sample.available_ram_bytes)
            )
            if sample.available_ram_bytes < self.minimum_ram_bytes:
                self.failure = self.failure or (
                    f"Available RAM {sample.available_ram_bytes} bytes fell below "
                    f"the evaluation floor {self.minimum_ram_bytes} bytes."
                )
            self._save()

    def _run(self):
        while not self._stop.is_set():
            try:
                sample = self._sampler()
                if self._stop.is_set():
                    return
                self._record(sample)
            except Exception as error:
                self._fail(f"Resource sampler failed: {type(error).__name__}: {error}")
            finally:
                self._ready.set()
            if self.failure is not None or self._stop.wait(self.interval):
                return

    def __enter__(self):
        if self._thread is not None:
            raise RuntimeError("A ResourceMonitor cannot be reused")
        self.output.mkdir(parents=True, exist_ok=True)
        self._shutdown = "running"
        self._thread = threading.Thread(target=self._run, name="evaluation-resources", daemon=True)
        self._thread.start()
        if not self._ready.wait(self.join_timeout):
            self._fail("Resource sampler did not produce an initial measurement in time")
        try:
            self.check()
        except EvaluationStop:
            self.close()
            raise
        return self

    def close(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=self.join_timeout)
        if self.running:
            self._shutdown = "timed_out"
            message = "Resource monitor shutdown timed out; sampler thread is still running"
            self._fail(message)
            raise EvaluationStop(message)
        with self._lock:
            self._shutdown = "stopped"
            try:
                self._save()
            except OSError as error:
                self.failure = self.failure or f"Unable to persist resource evidence: {error}"
        self.check()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False
