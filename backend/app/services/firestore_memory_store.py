from google.cloud import firestore

from app.models.memory import UserStrategyMemory


class FirestoreMemoryStore:
    """
    Firestore-backed storage for explicitly approved user strategies.

    Documents are partitioned by client_id:
    daisy_clients/{client_id}/strategies/{memory_id}
    """

    def __init__(self, client=None):
        self._client = client or firestore.Client()

    def _strategies_collection(self, client_id: str):
        return (
            self._client.collection("daisy_clients")
            .document(client_id)
            .collection("strategies")
        )

    def save(self, memory: UserStrategyMemory) -> None:
        self._strategies_collection(memory.client_id).document(memory.id).set(
            {
                "id": memory.id,
                "client_id": memory.client_id,
                "strategy": memory.strategy,
                "source": memory.source,
                "approved": memory.approved,
                "created_at": memory.created_at,
            }
        )

    def list_for_client(self, client_id: str) -> list[UserStrategyMemory]:
        client_id = client_id.strip()
        if not client_id:
            raise ValueError("client_id is required")

        memories = []

        for document in self._strategies_collection(client_id).stream():
            data = document.to_dict()

            memories.append(
                UserStrategyMemory(
                    id=data["id"],
                    client_id=client_id,
                    strategy=data["strategy"],
                    source=data["source"],
                    approved=data["approved"],
                    created_at=data["created_at"],
                )
            )

        return memories
