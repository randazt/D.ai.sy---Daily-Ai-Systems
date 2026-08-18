import unittest

from app.models.project import Task
from app.services.capability_registry import CapabilityRegistry
from app.services.task_executor import TaskExecutionResult, TaskExecutor


class DummyExecutor(TaskExecutor):
    async def execute(self, task: Task) -> TaskExecutionResult:
        return TaskExecutionResult(success=True, output=task.title)


class CapabilityRegistryTests(unittest.TestCase):
    def test_register_and_resolve(self):
        registry = CapabilityRegistry()
        executor = DummyExecutor()

        registry.register("reasoning", executor)
        resolved = registry.resolve("reasoning")

        self.assertIs(resolved, executor)

    def test_normalization_of_case_and_whitespace(self):
        registry = CapabilityRegistry()
        executor = DummyExecutor()
        registry.register(" Reasoning ", executor)

        self.assertIs(registry.resolve("reasoning"), executor)
        self.assertIs(registry.resolve(" REASONING "), executor)

    def test_none_resolves_to_reasoning(self):
        registry = CapabilityRegistry()
        executor = DummyExecutor()
        registry.register("reasoning", executor)

        self.assertIs(registry.resolve(None), executor)

    def test_empty_resolves_to_reasoning(self):
        registry = CapabilityRegistry()
        executor = DummyExecutor()
        registry.register("reasoning", executor)

        self.assertIs(registry.resolve(""), executor)

    def test_whitespace_only_resolves_to_reasoning(self):
        registry = CapabilityRegistry()
        executor = DummyExecutor()
        registry.register("reasoning", executor)

        self.assertIs(registry.resolve("   "), executor)

    def test_duplicate_registration_raises_value_error(self):
        registry = CapabilityRegistry()
        registry.register("reasoning", DummyExecutor())

        with self.assertRaises(ValueError):
            registry.register("reasoning", DummyExecutor())

    def test_supported_capabilities_returns_registered_values(self):
        registry = CapabilityRegistry()
        registry.register("reasoning", DummyExecutor())
        registry.register("research", DummyExecutor())

        self.assertEqual(
            registry.supported_capabilities(),
            ["reasoning", "research"],
        )

    def test_unknown_capability_resolves_none(self):
        registry = CapabilityRegistry()
        registry.register("reasoning", DummyExecutor())

        self.assertIsNone(registry.resolve("phone_call"))
