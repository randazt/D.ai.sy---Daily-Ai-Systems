from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class UserStrategyMemory:
    """
    A user-owned strategy that D.AI.SY may remember only after
    explicit human approval.

    This model stores a strategy the user has explicitly taught
    D.AI.SY. It must not be used to store diagnoses, inferred
    limitations, or hidden behavioral profiles.
    """

    id: str
    client_id: str
    strategy: str
    source: str
    approved: bool
    created_at: str

    @classmethod
    def create(cls, *, client_id: str, strategy: str):
        client_id = client_id.strip()
        strategy = strategy.strip()

        if not client_id:
            raise ValueError("client_id is required")
        if not strategy:
            raise ValueError("strategy is required")

        return cls(
            id=str(uuid4()),
            client_id=client_id,
            strategy=strategy,
            source="user_explicit",
            approved=True,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

