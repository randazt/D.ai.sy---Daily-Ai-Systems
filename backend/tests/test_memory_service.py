import unittest

from app.models.memory import UserStrategyMemory
from app.services.memory_service import (
    InMemoryMemoryStore,
    MemoryService,
    create_memory_store,
)


class MemoryServiceTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryMemoryStore()
        self.service = MemoryService(self.store)

    def test_remember_and_retrieve_approved_strategy(self):
        saved = self.service.remember_approved_strategy(
            client_id="client-a",
            strategy="Show me the whole system before the details.",
        )

        memories = self.service.get_approved_strategies(
            client_id="client-a",
        )

        self.assertEqual(memories, [saved])
        self.assertTrue(saved.approved)
        self.assertEqual(saved.source, "user_explicit")

    def test_memories_are_isolated_by_client(self):
        self.service.remember_approved_strategy(
            client_id="client-a",
            strategy="Show me the big picture first.",
        )
        self.service.remember_approved_strategy(
            client_id="client-b",
            strategy="Give me one step at a time.",
        )

        client_a_memories = self.service.get_approved_strategies(
            client_id="client-a",
        )

        self.assertEqual(len(client_a_memories), 1)
        self.assertEqual(
            client_a_memories[0].strategy,
            "Show me the big picture first.",
        )

    def test_retrieval_filters_nonapproved_or_nonexplicit_records(self):
        nonapproved = UserStrategyMemory(
            id="not-approved",
            client_id="client-a",
            strategy="Do not return this.",
            source="user_explicit",
            approved=False,
            created_at="2026-08-29T00:00:00+00:00",
        )
        inferred = UserStrategyMemory(
            id="inferred",
            client_id="client-a",
            strategy="Do not return this either.",
            source="inferred",
            approved=True,
            created_at="2026-08-29T00:00:00+00:00",
        )
        approved = UserStrategyMemory.create(
            client_id="client-a",
            strategy="Return this strategy.",
        )

        self.store.save(nonapproved)
        self.store.save(inferred)
        self.store.save(approved)

        memories = self.service.get_approved_strategies(
            client_id="client-a",
        )

        self.assertEqual(memories, [approved])

    def test_retrieval_rejects_empty_client_id(self):
        with self.assertRaisesRegex(ValueError, "client_id is required"):
            self.service.get_approved_strategies(client_id="   ")

    def test_create_memory_store_defaults_to_in_memory(self):
        store = create_memory_store(env={})

        self.assertIsInstance(store, InMemoryMemoryStore)

    def test_create_memory_store_accepts_explicit_in_memory(self):
        store = create_memory_store(
            env={"DAISY_MEMORY_STORE": "in_memory"}
        )

        self.assertIsInstance(store, InMemoryMemoryStore)

    def test_create_memory_store_rejects_unknown_backend(self):
        with self.assertRaisesRegex(
            ValueError,
            "Unsupported DAISY_MEMORY_STORE",
        ):
            create_memory_store(
                env={"DAISY_MEMORY_STORE": "mystery-store"}
            )

    def test_create_memory_store_selects_firestore(self):
        from app.services.firestore_memory_store import FirestoreMemoryStore

        store = create_memory_store(
            env={"DAISY_MEMORY_STORE": "firestore"}
        )

        self.assertIsInstance(store, FirestoreMemoryStore)


if __name__ == "__main__":
    unittest.main()