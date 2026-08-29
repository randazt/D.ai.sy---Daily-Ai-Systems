import unittest

from app.models.memory import UserStrategyMemory
from app.services.firestore_memory_store import FirestoreMemoryStore


class FakeDocumentSnapshot:
    def __init__(self, data):
        self._data = data

    def to_dict(self):
        return dict(self._data)


class FakeDocumentReference:
    def __init__(self, client, path):
        self._client = client
        self._path = path

    def collection(self, name):
        return FakeCollectionReference(
            self._client,
            f"{self._path}/{name}",
        )

    def set(self, data):
        self._client.documents[self._path] = dict(data)


class FakeCollectionReference:
    def __init__(self, client, path):
        self._client = client
        self._path = path

    def document(self, document_id):
        return FakeDocumentReference(
            self._client,
            f"{self._path}/{document_id}",
        )

    def stream(self):
        prefix = f"{self._path}/"
        return [
            FakeDocumentSnapshot(data)
            for path, data in self._client.documents.items()
            if path.startswith(prefix)
            and "/" not in path[len(prefix):]
        ]


class FakeFirestoreClient:
    def __init__(self):
        self.documents = {}

    def collection(self, name):
        return FakeCollectionReference(self, name)


class FirestoreMemoryStoreTests(unittest.TestCase):
    def setUp(self):
        self.client = FakeFirestoreClient()
        self.store = FirestoreMemoryStore(client=self.client)

    def test_save_uses_client_partitioned_document_path(self):
        memory = UserStrategyMemory.create(
            client_id="client-a",
            strategy="Show me the whole system first.",
        )

        self.store.save(memory)

        expected_path = f"daisy_clients/client-a/strategies/{memory.id}"
        self.assertIn(expected_path, self.client.documents)
        self.assertEqual(
            self.client.documents[expected_path]["strategy"],
            "Show me the whole system first.",
        )

    def test_list_for_client_reconstructs_saved_memory(self):
        memory = UserStrategyMemory.create(
            client_id="client-a",
            strategy="Give me the big picture first.",
        )
        self.store.save(memory)

        memories = self.store.list_for_client("client-a")

        self.assertEqual(memories, [memory])

    def test_list_for_client_isolates_clients(self):
        client_a = UserStrategyMemory.create(
            client_id="client-a",
            strategy="Strategy A",
        )
        client_b = UserStrategyMemory.create(
            client_id="client-b",
            strategy="Strategy B",
        )
        self.store.save(client_a)
        self.store.save(client_b)

        memories = self.store.list_for_client("client-a")

        self.assertEqual(memories, [client_a])

    def test_list_for_client_rejects_empty_client_id(self):
        with self.assertRaisesRegex(ValueError, "client_id is required"):
            self.store.list_for_client("   ")

    def test_path_client_is_authoritative_over_stored_client_id(self):
        memory = UserStrategyMemory.create(
            client_id="client-a",
            strategy="User-owned strategy.",
        )
        self.store.save(memory)

        path = f"daisy_clients/client-a/strategies/{memory.id}"
        self.client.documents[path]["client_id"] = "client-b"

        memories = self.store.list_for_client("client-a")

        self.assertEqual(memories[0].client_id, "client-a")


if __name__ == "__main__":
    unittest.main()
