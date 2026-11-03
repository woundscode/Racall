"""Add continuous memory cancellation and observe a separate user's Ollama."""

from urllib.parse import urlsplit

from model_evaluation03.guard import EvaluationStop, LiveGuard, local_endpoint


class MonitoredGuard(LiveGuard):
    def __init__(self, *args, monitor, observe_endpoint=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitor = monitor
        self.observe_endpoint = local_endpoint(observe_endpoint) if observe_endpoint else None
        # All accepted hosts are loopback; alternate spellings must not bypass
        # separation from the owner's server on the same TCP port.
        if self.observe_endpoint and (urlsplit(self.observe_endpoint).port or 80) == (
            urlsplit(self.endpoint).port or 80
        ):
            raise ValueError("The observed user server must differ from the evaluation server")

    def check(self):
        super().check()
        self.monitor.check()

    def runtime(self, label):
        import httpx

        self.check()
        if self.observe_endpoint:
            try:
                with httpx.Client(timeout=5, trust_env=False) as client:
                    loaded = (
                        client.get(self.observe_endpoint.removesuffix("/v1") + "/api/ps")
                        .raise_for_status()
                        .json()["models"]
                    )
                if not isinstance(loaded, list):
                    raise EvaluationStop("The user's Ollama returned an invalid loaded-model list")
                if loaded:
                    raise EvaluationStop("The user's Ollama has a loaded model; stop the separate test")
            except Exception as error:
                self.stop(f"User Ollama observation failed: {error}")
        return super().runtime(label)
