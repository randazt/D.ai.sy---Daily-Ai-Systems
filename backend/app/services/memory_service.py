import os
from collections.abc import Mapping
from typing import Protocol

from app.models.memory import UserStrategyMemory


class MemoryStore(Protocol):
    """
    Storage boundary for user-approved D.AI.SY memories.
    """

    def save(self, memory: UserStrategyMemory) -> None:
        ...

    def list_for_client(self, client_id: str) -> list[UserStrategyMemory]:
        ...


class InMemoryMemoryStore:
    """
    Local/test implementation of the memory store.
    """

    def __init__(self):
        self._memories: dict[str, list[UserStrategyMemory]] = {}

    def save(self, memory: UserStrategyMemory) -> None:
        self._memories.setdefault(memory.client_id, []).append(memory)

    def list_for_client(self, client_id: str) -> list[UserStrategyMemory]:
        return list(self._memories.get(client_id.strip(), []))


def create_memory_store(
    *,
    env: Mapping[str, str] | None = None,
) -> MemoryStore:
    """
    Select the configured memory backend.

    Firestore is imported lazily so local/test imports do not initialize
    Google Cloud infrastructure unless Firestore is explicitly selected.
    """
    environment = os.environ if env is None else env
    backend = environment.get("DAISY_MEMORY_STORE", "in_memory").strip().lower()

    if backend == "in_memory":
        return InMemoryMemoryStore()

    if backend == "firestore":
        from app.services.firestore_memory_store import FirestoreMemoryStore

        return FirestoreMemoryStore()

    raise ValueError(
        f"Unsupported DAISY_MEMORY_STORE: {backend!r}"
    )


class MemoryService:
    """
    Manages explicitly approved, user-owned strategies.

    Memory creation must occur only after the human has explicitly
    authorized D.AI.SY to remember the strategy.
    """

    def __init__(self, store: MemoryStore):
        self._store = store

    def remember_approved_strategy(
        self,
        *,
        client_id: str,
        strategy: str,
    ) -> UserStrategyMemory:
        memory = UserStrategyMemory.create(
            client_id=client_id,
            strategy=strategy,
        )
        self._store.save(memory)
        return memory

    def get_approved_strategies(
        self,
        *,
        client_id: str,
    ) -> list[UserStrategyMemory]:
        client_id = client_id.strip()
        if not client_id:
            raise ValueError("client_id is required")

        return [
            memory
            for memory in self._store.list_for_client(client_id)
            if memory.approved and memory.source == "user_explicit"
        ]


memory_service = MemoryService(create_memory_store())