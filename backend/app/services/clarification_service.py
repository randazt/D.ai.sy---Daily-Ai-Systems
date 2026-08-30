import base64
import hashlib
import hmac
import json
import os
import re
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from google.genai import types

from app.services.gemini_service import gemini_service


CLARIFICATION_TOKEN_SECRET_ENV = "DAISY_CLARIFICATION_TOKEN_SECRET"
CLARIFICATION_TOKEN_TTL_SECONDS = 15 * 60
TOKEN_PURPOSE = "clarification"
TOKEN_VERSION = 1
HUMAN_GATE_PASSED = "PASSED"
DECISION_CLEAR = "CLEAR"
DECISION_CLARIFY = "CLARIFY"
DECISION_DISCOVER_IN_PLAN = "DISCOVER_IN_PLAN"
VALID_DECISIONS = {
    DECISION_CLEAR,
    DECISION_CLARIFY,
    DECISION_DISCOVER_IN_PLAN,
}
CLARIFICATION_MODEL_SEED = 1

CLARIFICATION_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "decision": {
            "type": "string",
            "enum": [
                DECISION_CLEAR,
                DECISION_CLARIFY,
                DECISION_DISCOVER_IN_PLAN,
            ],
        },
        "missing_user_judgment": {"type": "string"},
        "why_planning_now_would_choose_for_user": {"type": "string"},
        "question": {"type": "string"},
    },
    "required": [
        "decision",
        "missing_user_judgment",
        "why_planning_now_would_choose_for_user",
        "question",
    ],
}

HUMAN_DECISION_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "has_user_value_conflict": {"type": "boolean"},
        "conflicting_priorities": {
            "type": "array",
            "items": {"type": "string"},
        },
        "can_external_evidence_resolve_it": {"type": "boolean"},
        "why_human_judgment_is_required": {"type": "string"},
        "question": {"type": "string"},
        "decision": {
            "type": "string",
            "enum": [
                DECISION_CLEAR,
                DECISION_CLARIFY,
                DECISION_DISCOVER_IN_PLAN,
            ],
        },
    },
    "required": [
        "has_user_value_conflict",
        "conflicting_priorities",
        "can_external_evidence_resolve_it",
        "why_human_judgment_is_required",
        "question",
    ],
}

PHONE_NUMBER_PATTERN = re.compile(r"(\+?[0-9][0-9\-\s().]{8,}[0-9])")
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(api[_ -]?key|token|secret|password|credential)\s*[:=]\s*\S+"
)


@dataclass(frozen=True)
class ClarificationDecision:
    needs_clarification: bool
    question: str = ""
    decision: str = ""
    missing_user_judgment: str = ""
    why_planning_now_would_choose_for_user: str = ""

    def __post_init__(self):
        decision = self.decision or (
            DECISION_CLARIFY if self.needs_clarification else DECISION_CLEAR
        )
        if decision not in VALID_DECISIONS:
            decision = DECISION_CLEAR

        object.__setattr__(self, "decision", decision)
        object.__setattr__(
            self,
            "needs_clarification",
            decision == DECISION_CLARIFY,
        )
        if decision != DECISION_CLARIFY:
            object.__setattr__(self, "question", "")
            object.__setattr__(self, "missing_user_judgment", "")
            object.__setattr__(
                self,
                "why_planning_now_would_choose_for_user",
                "",
            )


@dataclass(frozen=True)
class HumanDecisionGateOutcome:
    status: str
    clarification: ClarificationDecision | None = None


class ClarificationTokenError(Exception):
    pass


class ClarificationService:
    def __init__(
        self,
        *,
        token_secret_env: str = CLARIFICATION_TOKEN_SECRET_ENV,
        ttl_seconds: int = CLARIFICATION_TOKEN_TTL_SECONDS,
        now_provider=time.time,
        model_service=gemini_service,
    ):
        self._token_secret_env = token_secret_env
        self._ttl_seconds = ttl_seconds
        self._now_provider = now_provider
        self._model_service = model_service

    def evaluate(self, message: str) -> ClarificationDecision:
        cognitive_bottleneck_decision = (
            self._cognitive_bottleneck_decision(message)
        )
        if cognitive_bottleneck_decision is not None:
            return cognitive_bottleneck_decision

        human_decision = self._evaluate_human_decision_gate(message)
        if human_decision is not None:
            if human_decision.clarification is not None:
                return human_decision.clarification

            unformed_goal_decision = self._unformed_goal_decision(message)
            if unformed_goal_decision is not None:
                return unformed_goal_decision

            sufficiency_decision = self._deterministic_sufficiency_decision(
                message
            )
            if sufficiency_decision is not None:
                return sufficiency_decision

        model_decision = self._evaluate_with_model(message)
        if model_decision is not None:
            return model_decision

        return self._fallback_decision(message)

    def create_clarification_response(
        self,
        *,
        original_goal: str,
        question: str,
    ) -> dict[str, str]:
        token, expires_at = self.issue_token(
            original_goal=original_goal,
            question=question,
        )
        return {
            "agent": "clarification",
            "status": "needs_clarification",
            "question": question,
            "clarification_token": token,
            "expires_at": expires_at,
        }

    def invalid_context_response(
        self,
        message: str = "Clarification context is invalid or expired. Please restate your goal.",
    ) -> dict[str, str]:
        return {
            "agent": "clarification",
            "status": "invalid_context",
            "message": message,
        }

    def issue_token(self, *, original_goal: str, question: str) -> tuple[str, str]:
        secret = self._get_signing_secret()
        issued_at = int(self._now())
        expires_at = issued_at + self._ttl_seconds
        payload = {
            "v": TOKEN_VERSION,
            "purpose": TOKEN_PURPOSE,
            "clarification_id": str(uuid.uuid4()),
            "original_goal": self._sanitize_token_text(original_goal),
            "question": self._sanitize_token_text(question),
            "iat": issued_at,
            "exp": expires_at,
        }
        payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        payload_part = self._b64encode(payload_json.encode("utf-8"))
        signature = hmac.new(
            secret.encode("utf-8"),
            payload_part.encode("ascii"),
            hashlib.sha256,
        ).digest()
        token = f"{payload_part}.{self._b64encode(signature)}"

        return token, self._format_timestamp(expires_at)

    def validate_token(self, token: str) -> dict[str, Any]:
        secret = self._get_signing_secret()
        try:
            payload_part, signature_part = token.split(".", 1)
        except ValueError as e:
            raise ClarificationTokenError("Malformed clarification token.") from e

        try:
            provided_signature = self._b64decode(signature_part)
        except ValueError as e:
            raise ClarificationTokenError("Malformed clarification token.") from e

        expected_signature = hmac.new(
            secret.encode("utf-8"),
            payload_part.encode("ascii"),
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(provided_signature, expected_signature):
            raise ClarificationTokenError("Invalid clarification token signature.")

        try:
            payload = json.loads(self._b64decode(payload_part).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as e:
            raise ClarificationTokenError("Malformed clarification token.") from e

        self._validate_payload(payload)
        return payload

    def _evaluate_with_model(self, message: str) -> ClarificationDecision | None:
        prompt = f"""
You are D.A.I.S.Y.'s sufficiency and discovery classifier before planning.

The human-decision boundary is evaluated before this classifier. Do not use
this step to override unresolved user-value or user-preference conflicts.

Classify the planning request using this internal rubric:

CLEAR:
Enough user direction exists to construct a useful plan without D.A.I.S.Y.
choosing a consequential preference for the user.

CLARIFY:
Planning now would require D.A.I.S.Y. to choose a consequential user
preference, priority, objective, audience, constraint, or direction that the
human should decide.

DISCOVER_IN_PLAN:
Relevant information is unknown, but discovering, comparing, testing,
researching, or validating it belongs inside the requested plan.

Locked principle:
Uncertainty is NOT the same as underspecification.

Ask: If D.A.I.S.Y. planned now, would it have to choose an important direction
on the user's behalf?

Explicit planning presumption:
If the user explicitly asks for a plan and provides an actionable planning
objective, presume the request is sufficient. Override that presumption only
when proceeding still requires a consequential user preference or direction
decision.

DO NOT clarify merely because:
- the user says "I'm not sure"
- the user does not know whether an idea will work
- market/customer facts are unknown
- validation results are unknown
- the plan is intended to discover the missing information
- implementation details are unknown but can become tasks
- the goal is broad but can be decomposed without choosing an important
  preference for the user

DO clarify when:
- materially different plans depend on an unresolved user preference
- proceeding would select a major objective, priority, audience, constraint, or
  direction that belongs to the human
- D.A.I.S.Y. cannot construct a responsible useful plan without making that
  choice for the user

Return JSON only:
{{
  "decision": "CLEAR | CLARIFY | DISCOVER_IN_PLAN",
  "missing_user_judgment": "string, required for CLARIFY, otherwise empty",
  "why_planning_now_would_choose_for_user": "string, required for CLARIFY, otherwise empty",
  "question": "exactly one concise question for CLARIFY, otherwise empty"
}}

For CLARIFY, all three explanation/question fields must be non-empty.
For CLEAR and DISCOVER_IN_PLAN, question must be empty.

User message:
{message}
"""
        try:
            response = self._model_service.generate(
                prompt,
                config=self._classification_config(),
            )
        except Exception:
            return None

        if not isinstance(response, dict):
            return None

        reply = response.get("reply")
        if not isinstance(reply, str):
            return None

        payload = self._parse_json_payload(reply)
        if not isinstance(payload, dict):
            return None

        decision = self._normalize_decision(payload.get("decision"))
        if decision is None:
            needs_clarification = payload.get("needs_clarification")
            if not isinstance(needs_clarification, bool):
                return None
            decision = (
                DECISION_CLARIFY
                if needs_clarification
                else DECISION_CLEAR
            )

        if decision != DECISION_CLARIFY:
            return self._decision(decision)

        question = self._normalize_question(payload.get("question"))
        missing_user_judgment = self._normalize_text(
            payload.get("missing_user_judgment")
        )
        why_choose_for_user = self._normalize_text(
            payload.get("why_planning_now_would_choose_for_user")
        )
        if not question or not missing_user_judgment or not why_choose_for_user:
            return None

        return self._decision(
            DECISION_CLARIFY,
            question=question,
            missing_user_judgment=missing_user_judgment,
            why_planning_now_would_choose_for_user=why_choose_for_user,
        )

    def _evaluate_human_decision_gate(
        self,
        message: str,
    ) -> HumanDecisionGateOutcome | None:
        prompt = f"""
You are D.A.I.S.Y.'s human-decision boundary before planning.

This is not a general ambiguity detector. Evaluate only this question:

Would constructing the requested plan require choosing among materially
different legitimate directions based primarily on a preference, value,
priority, acceptable trade-off, objective, or governing direction that belongs
to the user?

USER-VALUE CONFLICT:
External evidence can explain consequences of the options, but cannot determine
which outcome the human values more.

EVIDENCE-RESOLVABLE UNCERTAINTY:
The unresolved question can be investigated through research, comparison,
testing, reasoning, or validation. That is not a user-value conflict.

Analyzing, comparing, explaining, or planning around both sides of a trade-off
does NOT eliminate the need for human clarification when the eventual plan must
optimize for a user-defined priority.

D.A.I.S.Y. may help the human understand a trade-off. D.A.I.S.Y. must not
silently decide which legitimate personal priority should govern the plan.

Return JSON only:
{{
  "has_user_value_conflict": true|false,
  "conflicting_priorities": ["string", "..."],
  "can_external_evidence_resolve_it": true|false,
  "why_human_judgment_is_required": "string, required when human judgment is required, otherwise empty",
  "question": "exactly one concise clarification question when human judgment is required, otherwise empty",
  "decision": "optional diagnostic label"
}}

If has_user_value_conflict is true and can_external_evidence_resolve_it is
false, provide at least two conflicting priorities, one concise question, and a
reason human judgment is required.

User message:
{message}
"""
        try:
            response = self._model_service.generate(
                prompt,
                config=self._human_decision_config(),
            )
        except Exception:
            return None

        if not isinstance(response, dict):
            return None

        reply = response.get("reply")
        if not isinstance(reply, str):
            return None

        payload = self._parse_json_payload(reply)
        if not isinstance(payload, dict):
            return None

        has_conflict = payload.get("has_user_value_conflict")
        can_evidence_resolve = payload.get("can_external_evidence_resolve_it")
        if not isinstance(has_conflict, bool) or not isinstance(
            can_evidence_resolve,
            bool,
        ):
            return None

        if not has_conflict or can_evidence_resolve:
            return HumanDecisionGateOutcome(status=HUMAN_GATE_PASSED)

        priorities = self._normalize_string_list(
            payload.get("conflicting_priorities")
        )
        reason = self._normalize_text(
            payload.get("why_human_judgment_is_required")
        )
        question = self._normalize_question(payload.get("question"))
        if len(priorities) < 2 or not reason or not question:
            return None

        return HumanDecisionGateOutcome(
            status=DECISION_CLARIFY,
            clarification=self._decision(
                DECISION_CLARIFY,
                question=question,
                missing_user_judgment="; ".join(priorities),
                why_planning_now_would_choose_for_user=reason,
            ),
        )

    @classmethod
    def _cognitive_bottleneck_decision(
        cls,
        message: str,
    ) -> ClarificationDecision | None:
        text = cls._normalized_message(message)
        if not text:
            return None

        cognition_first_phrases = (
            "help me figure out what's actually making this hard",
            "help me figure out what is actually making this hard",
            "help me understand what's making this hard",
            "help me understand what is making this hard",
            "figure out what's making this hard",
            "figure out what is making this hard",
        )

        explicit_cognition_first = any(
            phrase in text
            for phrase in cognition_first_phrases
        )

        overwhelm_markers = (
            "everything feels equally important",
            "everything seems equally important",
            "everything feels important",
            "don't know where to start",
            "do not know where to start",
        )
        organizing_markers = (
            "organizing my week",
            "organize my week",
            "planning my week",
            "plan my week",
        )
        system_request_markers = (
            "turn this into a simple system",
            "turn this into a system",
            "help me build a system",
            "help me create a system",
        )

        everyday_overwhelm_request = (
            any(marker in text for marker in overwhelm_markers)
            and any(marker in text for marker in organizing_markers)
            and any(marker in text for marker in system_request_markers)
        )

        if not explicit_cognition_first and not everyday_overwhelm_request:
            return None

        return ClarificationDecision(
            needs_clarification=True,
            decision="CLARIFY",
            question=(
                "When you look at everything you need to do, where do you "
                "get stuck first: deciding what matters most, choosing "
                "between things that all feel important, or holding too "
                "many things in your head at once?"
            ),
            missing_user_judgment=(
                "The user wants help understanding the cognitive bottleneck "
                "before D.AI.SY turns it into a system or plan."
            ),
            why_planning_now_would_choose_for_user=(
                "D.AI.SY should understand the bottleneck before introducing "
                "a planning tradeoff or deciding how the problem should be "
                "structured."
            ),
        )

    @classmethod
    def _unformed_goal_decision(
        cls,
        message: str,
    ) -> ClarificationDecision | None:
        text = cls._normalized_message(message)
        if not text:
            return None

        if cls._has_explicit_planning_objective(text):
            return None

        exploratory_creation_markers = (
            "idea",
            "build",
            "create",
            "make",
            "develop",
            "start",
        )
        unformed_goal_markers = (
            "all over the place",
            "don't know what",
            "do not know what",
            "don't know how to turn",
            "do not know how to turn",
            "don't know where to start",
            "do not know where to start",
            "not sure what",
            "unclear what",
            "figure out what",
        )

        has_creation_intent = any(
            marker in text for marker in exploratory_creation_markers
        )
        has_unformed_goal = any(
            marker in text for marker in unformed_goal_markers
        )

        if not has_creation_intent or not has_unformed_goal:
            return None

        return cls._decision(
            DECISION_CLARIFY,
            question=(
                "What feels clearest right now: what you want to create, "
                "who you want it to help, or why it matters to you?"
            ),
            missing_user_judgment=(
                "The user has expressed intent to create or build something, "
                "but has not yet formed enough of the goal for planning to "
                "begin without D.AI.S.Y. supplying the direction."
            ),
            why_planning_now_would_choose_for_user=(
                "Planning now would turn an early, still-forming idea into a "
                "specific direction before the user has established what "
                "they want to create, who it should help, or why it matters."
            ),
        )

    def _fallback_decision(self, message: str) -> ClarificationDecision:
        text = self._normalized_message(message)
        if self._requests_discovery_in_plan(text):
            return self._decision(DECISION_DISCOVER_IN_PLAN)
        return self._decision(DECISION_CLEAR)

    @classmethod
    def _deterministic_sufficiency_decision(
        cls,
        message: str,
    ) -> ClarificationDecision | None:
        text = cls._normalized_message(message)
        if not text:
            return cls._decision(DECISION_CLEAR)

        if cls._requests_discovery_in_plan(text):
            return cls._decision(DECISION_DISCOVER_IN_PLAN)

        if cls._has_explicit_planning_objective(text):
            return cls._decision(DECISION_CLEAR)

        return None

    @staticmethod
    def _classification_config() -> types.GenerateContentConfig:
        return ClarificationService._generation_config(
            CLARIFICATION_RESPONSE_SCHEMA
        )

    @staticmethod
    def _human_decision_config() -> types.GenerateContentConfig:
        return ClarificationService._generation_config(
            HUMAN_DECISION_RESPONSE_SCHEMA
        )

    @staticmethod
    def _generation_config(
        response_schema: dict[str, Any],
    ) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            temperature=0,
            seed=CLARIFICATION_MODEL_SEED,
            responseMimeType="application/json",
            responseSchema=response_schema,
        )

    @classmethod
    def _decision(
        cls,
        decision: str,
        *,
        question: str = "",
        missing_user_judgment: str = "",
        why_planning_now_would_choose_for_user: str = "",
    ) -> ClarificationDecision:
        return ClarificationDecision(
            needs_clarification=decision == DECISION_CLARIFY,
            question=question,
            decision=decision,
            missing_user_judgment=missing_user_judgment,
            why_planning_now_would_choose_for_user=(
                why_planning_now_would_choose_for_user
            ),
        )

    @classmethod
    def _clarify_decision(cls) -> ClarificationDecision:
        return cls._decision(
            DECISION_CLARIFY,
            question=cls._fallback_question(),
            missing_user_judgment=(
                "The user has not chosen the priority or direction the plan "
                "should optimize for."
            ),
            why_planning_now_would_choose_for_user=(
                "Planning now would select among materially different paths "
                "without the user's preference."
            ),
        )

    @staticmethod
    def _normalized_message(message: str) -> str:
        return " ".join(message.lower().split())

    @classmethod
    def _has_explicit_planning_objective(cls, text: str) -> bool:
        planning_markers = (
            "plan",
            "project",
            "strategy",
            "roadmap",
            "steps",
            "step",
        )
        return any(marker in text for marker in planning_markers)

    @classmethod
    def _requests_discovery_in_plan(cls, text: str) -> bool:
        if not cls._has_explicit_planning_objective(text):
            return False

        uncertainty_markers = (
            "i'm not sure",
            "i am not sure",
            "don't know",
            "do not know",
            "unknown",
            "unclear",
            "not sure",
            "need to understand",
        )
        discovery_markers = (
            "compare",
            "test",
            "validate",
            "validation",
            "research",
            "discover",
            "find out",
            "evaluate",
            "assess",
            "estimate",
        )
        return any(marker in text for marker in uncertainty_markers) and any(
            marker in text for marker in discovery_markers
        )

    @staticmethod
    def _fallback_question() -> str:
        return (
            "Which priority or direction should the plan optimize for first?"
        )

    @classmethod
    def _normalize_question(cls, value: object) -> str:
        if not isinstance(value, str):
            return ""

        text = " ".join(value.strip().split())
        if not text:
            return ""

        question_index = text.find("?")
        if question_index != -1:
            text = text[: question_index + 1]
        elif len(text) > 240:
            text = text[:240].rstrip()

        if not text.endswith("?"):
            text = f"{text}?"

        return text

    @staticmethod
    def _parse_json_payload(reply: str) -> object | None:
        text = reply.strip()
        if not text:
            return None

        fenced_match = re.search(
            r"```(?:json)?\s*(.*?)```",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        candidates = [fenced_match.group(1).strip()] if fenced_match else []
        candidates.append(text)

        start_index = text.find("{")
        if start_index != -1:
            candidates.append(text[start_index:])

        for candidate in candidates:
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue

        return None

    @staticmethod
    def _normalize_decision(value: object) -> str | None:
        if not isinstance(value, str):
            return None

        decision = value.strip().upper()
        if decision in VALID_DECISIONS:
            return decision
        return None

    @staticmethod
    def _normalize_text(value: object) -> str:
        if not isinstance(value, str):
            return ""
        return " ".join(value.strip().split())

    @staticmethod
    def _normalize_string_list(value: object) -> list[str]:
        if not isinstance(value, list):
            return []

        strings: list[str] = []
        for item in value:
            if not isinstance(item, str):
                continue
            text = " ".join(item.strip().split())
            if text and text not in strings:
                strings.append(text)
        return strings

    def _validate_payload(self, payload: object) -> None:
        if not isinstance(payload, dict):
            raise ClarificationTokenError("Malformed clarification token.")

        if payload.get("v") != TOKEN_VERSION:
            raise ClarificationTokenError("Unsupported clarification token version.")
        if payload.get("purpose") != TOKEN_PURPOSE:
            raise ClarificationTokenError("Invalid clarification token purpose.")
        if not isinstance(payload.get("clarification_id"), str):
            raise ClarificationTokenError("Malformed clarification token.")
        if not isinstance(payload.get("original_goal"), str):
            raise ClarificationTokenError("Malformed clarification token.")
        if not isinstance(payload.get("question"), str):
            raise ClarificationTokenError("Malformed clarification token.")

        expires_at = payload.get("exp")
        if not isinstance(expires_at, int):
            raise ClarificationTokenError("Malformed clarification token.")
        if expires_at <= int(self._now()):
            raise ClarificationTokenError("Clarification token expired.")

    def _get_signing_secret(self) -> str:
        secret = os.getenv(self._token_secret_env)
        if not secret:
            raise ClarificationTokenError(
                "Clarification signing secret is unavailable."
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
    def _sanitize_token_text(text: str) -> str:
        sanitized = PHONE_NUMBER_PATTERN.sub("[redacted-phone]", text)
        sanitized = SECRET_ASSIGNMENT_PATTERN.sub(r"\1=[redacted]", sanitized)
        return sanitized

    @staticmethod
    def _b64encode(value: bytes) -> str:
        return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")

    @staticmethod
    def _b64decode(value: str) -> bytes:
        padding = "=" * (-len(value) % 4)
        try:
            return base64.urlsafe_b64decode(f"{value}{padding}")
        except Exception as e:
            raise ValueError("Invalid base64 value.") from e


clarification_service = ClarificationService()