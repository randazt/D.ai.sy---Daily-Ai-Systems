import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime

from app.models.memory import UserStrategyMemory


class UserStrategyMemoryTests(unittest.TestCase):
    def test_create_builds_explicit_approved_memory(self):
        memory = UserStrategyMemory.create(
            client_id="test-client",
            strategy="Seeing the whole system first helps me learn.",
        )

        self.assertEqual(memory.client_id, "test-client")
        self.assertEqual(
            memory.strategy,
            "Seeing the whole system first helps me learn.",
        )
        self.assertEqual(memory.source, "user_explicit")
        self.assertTrue(memory.approved)
        self.assertTrue(memory.id)
        datetime.fromisoformat(memory.created_at)

    def test_create_strips_strategy_whitespace(self):
        memory = UserStrategyMemory.create(
            client_id="test-client",
            strategy="  Show me the big picture first.  ",
        )

        self.assertEqual(memory.strategy, "Show me the big picture first.")

    def test_each_memory_receives_unique_id(self):
        first = UserStrategyMemory.create(
            client_id="test-client",
            strategy="Show me the big picture first.",
        )
        second = UserStrategyMemory.create(
            client_id="test-client",
            strategy="Break complex work into smaller steps.",
        )

        self.assertNotEqual(first.id, second.id)

    def test_memory_is_immutable(self):
        memory = UserStrategyMemory.create(
            client_id="test-client",
            strategy="Show me the big picture first.",
        )

        with self.assertRaises(FrozenInstanceError):
            memory.strategy = "Changed without approval."


    def test_create_rejects_empty_client_id(self):
        with self.assertRaisesRegex(ValueError, "client_id is required"):
            UserStrategyMemory.create(
                client_id="   ",
                strategy="Show me the big picture first.",
            )

    def test_create_rejects_empty_strategy(self):
        with self.assertRaisesRegex(ValueError, "strategy is required"):
            UserStrategyMemory.create(
                client_id="test-client",
                strategy="   ",
            )
if __name__ == "__main__":
    unittest.main()

