import os
import unittest
from unittest.mock import patch

from app.services.memory_authorization_service import (
    MEMORY_AUTHORIZATION_SECRET_ENV,
    MemoryAuthorizationError,
    MemoryAuthorizationService,
)


TEST_SECRET = "test-memory-authorization-secret"


class MemoryAuthorizationServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = MemoryAuthorizationService(
            now_provider=lambda: 1000.0,
            ttl_seconds=300,
        )

    def test_proposal_contains_exact_strategy_and_signed_token(self):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            proposal = self.service.create_proposal(
                client_id="client-a",
                strategy="Show me the whole system before the details.",
            )

        self.assertEqual(
            proposal["strategy"],
            "Show me the whole system before the details.",
        )
        self.assertTrue(proposal["memory_token"])
        self.assertTrue(proposal["expires_at"])

    def test_valid_token_returns_exact_signed_client_and_strategy(self):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            proposal = self.service.create_proposal(
                client_id="client-a",
                strategy="Show me the big picture first.",
            )

            payload = self.service.validate_token(
                proposal["memory_token"]
            )

        self.assertEqual(payload["client_id"], "client-a")
        self.assertEqual(
            payload["strategy"],
            "Show me the big picture first.",
        )
        self.assertEqual(
            payload["purpose"],
            "memory_strategy_approval",
        )

    def test_proposal_normalizes_client_id_and_strategy(self):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            proposal = self.service.create_proposal(
                client_id="  client-a  ",
                strategy="  Show me the whole system first.  ",
            )

            payload = self.service.validate_token(
                proposal["memory_token"]
            )

        self.assertEqual(payload["client_id"], "client-a")
        self.assertEqual(
            payload["strategy"],
            "Show me the whole system first.",
        )

    def test_proposal_rejects_empty_client_id(self):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "client_id is required",
            ):
                self.service.create_proposal(
                    client_id="   ",
                    strategy="Show me the big picture first.",
                )

    def test_proposal_rejects_empty_strategy(self):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "strategy is required",
            ):
                self.service.create_proposal(
                    client_id="client-a",
                    strategy="   ",
                )

    def test_tampered_token_fails_closed(self):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            proposal = self.service.create_proposal(
                client_id="client-a",
                strategy="Show me the big picture first.",
            )
            token = proposal["memory_token"]

            payload_part, signature_part = token.split(".", 1)
            replacement = "A" if payload_part[0] != "A" else "B"
            tampered_payload = replacement + payload_part[1:]
            tampered_token = (
                f"{tampered_payload}.{signature_part}"
            )

            with self.assertRaises(MemoryAuthorizationError):
                self.service.validate_token(tampered_token)

    def test_malformed_token_fails_closed(self):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            with self.assertRaises(MemoryAuthorizationError):
                self.service.validate_token("not-a-token")

    def test_expired_token_fails_closed(self):
        issuing_service = MemoryAuthorizationService(
            now_provider=lambda: 1000.0,
            ttl_seconds=1,
        )

        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            proposal = issuing_service.create_proposal(
                client_id="client-a",
                strategy="Show me the big picture first.",
            )

            validating_service = MemoryAuthorizationService(
                now_provider=lambda: 1002.0,
                ttl_seconds=300,
            )

            with self.assertRaisesRegex(
                MemoryAuthorizationError,
                "expired",
            ):
                validating_service.validate_token(
                    proposal["memory_token"]
                )

    def test_missing_secret_fails_closed_when_creating_proposal(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop(MEMORY_AUTHORIZATION_SECRET_ENV, None)

            with self.assertRaisesRegex(
                MemoryAuthorizationError,
                "signing secret is unavailable",
            ):
                self.service.create_proposal(
                    client_id="client-a",
                    strategy="Show me the big picture first.",
                )

    def test_missing_secret_fails_closed_when_validating_token(self):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            proposal = self.service.create_proposal(
                client_id="client-a",
                strategy="Show me the big picture first.",
            )

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop(MEMORY_AUTHORIZATION_SECRET_ENV, None)

            with self.assertRaisesRegex(
                MemoryAuthorizationError,
                "signing secret is unavailable",
            ):
                self.service.validate_token(
                    proposal["memory_token"]
                )

    def test_token_from_different_secret_is_rejected(self):
        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: TEST_SECRET},
            clear=False,
        ):
            proposal = self.service.create_proposal(
                client_id="client-a",
                strategy="Show me the big picture first.",
            )

        with patch.dict(
            os.environ,
            {MEMORY_AUTHORIZATION_SECRET_ENV: "different-secret"},
            clear=False,
        ):
            with self.assertRaises(MemoryAuthorizationError):
                self.service.validate_token(
                    proposal["memory_token"]
                )


if __name__ == "__main__":
    unittest.main()