from app.services.task_executor import TaskExecutor


class CapabilityRegistry:
    def __init__(self):
        self._executors: dict[str, TaskExecutor] = {}

    def register(self, capability: str, executor: TaskExecutor) -> None:
        normalized = self._normalize(capability)

        if normalized in self._executors:
            raise ValueError(
                f"Executor already registered for capability: {normalized}"
            )

        self._executors[normalized] = executor

    def resolve(self, capability: str | None) -> TaskExecutor | None:
        normalized = self._normalize(capability)
        return self._executors.get(normalized)

    def supported_capabilities(self) -> list[str]:
        return list(self._executors.keys())

    @staticmethod
    def _normalize(capability: str | None) -> str:
        if capability is None:
            return "reasoning"

        normalized = capability.strip().lower()
        if not normalized:
            return "reasoning"

        return normalized
