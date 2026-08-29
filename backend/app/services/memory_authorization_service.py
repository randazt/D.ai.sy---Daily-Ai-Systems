import base64
import hashlib
import hmac
import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable


MEMORY_AUTHORIZATION_SECRET_ENV = "DAISY_MEMORY_AUTHORIZATION_SECRET"
MEMORY_TOKEN_VERSION = 1
MEMORY_TOKEN_PURPOSE = "memory_strategy_approval"
DEFAULT_MEMORY_TOKEN_TTL_SECONDS = 300


class MemoryAuthorizationError(ValueError):
    """
    Raised when a memory authorization proposal cannot be created
    or when a memory authorization token fails validation.
    """


class MemoryAuthorizationService:
    """
    Creates and validates short-lived authorization proposals for
    persistent user-owned strategy memory.

    A proposal binds the exact client identity and exact strategy
    presented to the human. Persistence happens elsewhere, only
    after this signed proposal has been explicitly approved.
    """

    def __init__(
        self,
        *,
        token_secret_env: str = MEMORY_AUTHORIZATION_SECRET_ENV,
        ttl_seconds: int = DEFAULT_MEMORY_TOKEN_TTL_SECONDS,
        now_provider: Callable[[], float] = time.time,
    ):
        self._token_secret_env = token_secret_env
        self._ttl_seconds = ttl_seconds
        self._now_provider = now_provider

    def create_proposal(
        self,
        *,
        client_id: str,
        strategy: str,
    ) -> dict[str, str]:
        normalized_client_id = client_id.strip()
        normalized_strategy = strategy.strip()

        if not normalized_client_id:
            raise ValueError("client_id is required")
        if not normalized_strategy:
            raise ValueError("strategy is required")

        secret = self._get_signing_secret()
        issued_at = int(self._now())
        expires_at = issued_at + self._ttl_seconds

        payload = {
            "v": MEMORY_TOKEN_VERSION,
            "purpose": MEMORY_TOKEN_PURPOSE,
            "proposal_id": str(uuid.uuid4()),
            "client_id": normalized_client_id,
            "strategy": normalized_strategy,
            "iat": issued_at,
            "exp": expires_at,
        }

        payload_json = json.dumps(
            payload,
            separators=(",", ":"),
            sort_keys=True,
        )
        payload_part = self._b64encode(
            payload_json.encode("utf-8")
        )

        signature = hmac.new(
            secret.encode("utf-8"),
            payload_part.encode("ascii"),
            hashlib.sha256,
        ).digest()

        token = (
            f"{payload_part}."
            f"{self._b64encode(signature)}"
        )

        return {
            "strategy": normalized_strategy,
            "memory_token": token,
            "expires_at": self._format_timestamp(expires_at),
        }

    def validate_token(self, token: str) -> dict[str, Any]:
        secret = self._get_signing_secret()

        try:
            payload_part, signature_part = token.split(".", 1)
        except ValueError as exc:
            raise MemoryAuthorizationError(
                "Malformed memory authorization token."
            ) from exc

        if not payload_part or not signature_part:
            raise MemoryAuthorizationError(
                "Malformed memory authorization token."
            )

        try:
            provided_signature = self._b64decode(signature_part)
        except ValueError as exc:
            raise MemoryAuthorizationError(
                "Malformed memory authorization token."
            ) from exc

        expected_signature = hmac.new(
            secret.encode("utf-8"),
            payload_part.encode("ascii"),
            hashlib.sha256,
        ).digest()

        if not hmac.compare_digest(
            provided_signature,
            expected_signature,
        ):
            raise MemoryAuthorizationError(
                "Invalid memory authorization token signature."
            )

        try:
            payload_bytes = self._b64decode(payload_part)
            payload = json.loads(payload_bytes.decode("utf-8"))
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
            ValueError,
        ) as exc:
            raise MemoryAuthorizationError(
                "Malformed memory authorization token."
            ) from exc

        self._validate_payload(payload)
        return payload

    def _validate_payload(self, payload: object) -> None:
        if not isinstance(payload, dict):
            raise MemoryAuthorizationError(
                "Malformed memory authorization token."
            )

        if payload.get("v") != MEMORY_TOKEN_VERSION:
            raise MemoryAuthorizationError(
                "Unsupported memory authorization token version."
            )

        if payload.get("purpose") != MEMORY_TOKEN_PURPOSE:
            raise MemoryAuthorizationError(
                "Invalid memory authorization token purpose."
            )

        proposal_id = payload.get("proposal_id")
        if not isinstance(proposal_id, str) or not proposal_id.strip():
            raise MemoryAuthorizationError(
                "Malformed memory authorization token."
            )

        client_id = payload.get("client_id")
        if not isinstance(client_id, str) or not client_id.strip():
            raise MemoryAuthorizationError(
                "Malformed memory authorization token."
            )

        strategy = payload.get("strategy")
        if not isinstance(strategy, str) or not strategy.strip():
            raise MemoryAuthorizationError(
                "Malformed memory authorization token."
            )

        issued_at = payload.get("iat")
        expires_at = payload.get("exp")

        if not isinstance(issued_at, int):
            raise MemoryAuthorizationError(
                "Malformed memory authorization token."
            )

        if not isinstance(expires_at, int):
            raise MemoryAuthorizationError(
                "Malformed memory authorization token."
            )

        if expires_at <= issued_at:
            raise MemoryAuthorizationError(
                "Malformed memory authorization token."
            )

        if expires_at <= int(self._now()):
            raise MemoryAuthorizationError(
                "Memory authorization token expired."
            )

    def _get_signing_secret(self) -> str:
        secret = os.getenv(self._token_secret_env)

        if not secret:
            raise MemoryAuthorizationError(
                "Memory authorization signing secret is unavailable."
            )

        return secret

    def _now(self) -> float:
        return float(self._now_provider())

    @staticmethod
    def _format_timestamp(timestamp: int) -> str:
        return (
            datetime.fromtimestamp(timestamp, timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )

    @staticmethod
    def _b64encode(value: bytes) -> str:
        return (
            base64.urlsafe_b64encode(value)
            .decode("ascii")
            .rstrip("=")
        )

    @staticmethod
    def _b64decode(value: str) -> bytes:
        padding = "=" * (-len(value) % 4)

        try:
            return base64.urlsafe_b64decode(
                f"{value}{padding}"
            )
        except Exception as exc:
            raise ValueError(
                "Invalid base64 value."
            ) from exc


memory_authorization_service = MemoryAuthorizationService()