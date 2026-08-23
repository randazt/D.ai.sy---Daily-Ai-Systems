import unittest

from app.main import app


PUBLIC_RESPONSE_VARIANTS = {
    "PlannerResponse",
    "ExecutionResponse",
    "AgentStatusMessageResponse",
    "ClarificationResponse",
    "ConversationResponse",
}
SUPPORTED_OUTCOMES = {
    "completed",
    "failed",
    "unsupported",
    "authority_required",
}
SUPPORTED_DECISIONS = {
    "continue",
    "retry",
    "replan",
    "request_authority",
    "stop",
}


def _referenced_schema_names(value):
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            yield ref.rsplit("/", 1)[-1]
        for child in value.values():
            yield from _referenced_schema_names(child)
    elif isinstance(value, list):
        for child in value:
            yield from _referenced_schema_names(child)


def _property_names(value):
    names = set()
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            names.update(properties)
        for child in value.values():
            names.update(_property_names(child))
    elif isinstance(value, list):
        for child in value:
            names.update(_property_names(child))
    return names


def _enum_values(value):
    values = set()
    if isinstance(value, dict):
        enum = value.get("enum")
        if isinstance(enum, list):
            values.update(enum)
        for child in value.values():
            values.update(_enum_values(child))
    elif isinstance(value, list):
        for child in value:
            values.update(_enum_values(child))
    return values


class OpenAPIDocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.openapi = app.openapi()
        cls.schemas = cls.openapi["components"]["schemas"]
        cls.chat_post = cls.openapi["paths"]["/chat"]["post"]

    def test_post_chat_exists(self):
        self.assertIn("/chat", self.openapi["paths"])
        self.assertIn("post", self.openapi["paths"]["/chat"])

    def test_chat_200_response_has_json_schema(self):
        response = self.chat_post["responses"]["200"]
        json_content = response["content"]["application/json"]
        self.assertIsInstance(json_content["schema"], dict)

    def test_chat_200_response_has_exact_public_variants(self):
        response_schema = self.chat_post["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        any_of = response_schema["anyOf"]
        variants = [item["$ref"].rsplit("/", 1)[-1] for item in any_of]

        self.assertEqual(len(variants), len(PUBLIC_RESPONSE_VARIANTS))
        self.assertEqual(set(variants), PUBLIC_RESPONSE_VARIANTS)

    def test_planner_task_schema_exposes_public_fields(self):
        properties = self.schemas["PlannerTaskSchema"]["properties"]
        expected = {
            "title",
            "description",
            "capability",
            "inputs",
            "status",
            "output",
        }
        self.assertTrue(expected.issubset(properties))

    def test_execution_current_task_schema_exposes_public_fields(self):
        properties = self.schemas["ExecutionCurrentTaskSchema"]["properties"]
        expected = {
            "title",
            "description",
            "capability",
            "inputs",
            "status",
            "output",
            "observation",
        }
        self.assertTrue(expected.issubset(properties))

    def test_task_observation_schema_exposes_public_fields(self):
        properties = self.schemas["TaskObservationSchema"]["properties"]
        expected = {
            "task_title",
            "capability",
            "status",
            "success",
            "outcome",
            "summary",
            "error",
        }
        self.assertTrue(expected.issubset(properties))

    def test_task_observation_outcome_contract(self):
        outcome = self.schemas["TaskObservationSchema"]["properties"]["outcome"]
        documented_values = _enum_values(outcome)

        if documented_values:
            self.assertEqual(documented_values, SUPPORTED_OUTCOMES)
        else:
            self.assertEqual(outcome.get("type"), "string")

    def test_task_decision_schema_exposes_public_fields(self):
        properties = self.schemas["TaskDecisionSchema"]["properties"]
        expected = {
            "decision",
            "reason",
        }

        self.assertEqual(set(properties), expected)

    def test_task_decision_schema_uses_exact_decision_enum(self):
        decision = self.schemas["TaskDecisionSchema"]["properties"]["decision"]
        documented_values = _enum_values(decision)

        self.assertEqual(documented_values, SUPPORTED_DECISIONS)

    def test_execution_response_exposes_optional_decision(self):
        properties = self.schemas["ExecutionResponse"]["properties"]
        decision = properties["decision"]

        self.assertIn("decision", properties)
        self.assertEqual(
            decision["anyOf"][0]["$ref"],
            "#/components/schemas/TaskDecisionSchema",
        )

    def test_execution_response_exposes_optional_continuation(self):
        properties = self.schemas["ExecutionResponse"]["properties"]
        continuation = properties["continuation"]

        self.assertIn("continuation", properties)
        self.assertEqual(
            continuation["anyOf"][0]["$ref"],
            "#/components/schemas/ExecutionContinuationSchema",
        )

    def test_execution_continuation_schema_exposes_public_fields(self):
        properties = self.schemas["ExecutionContinuationSchema"]["properties"]
        expected = {
            "continue_applied",
            "continue_skipped_reason",
            "continued_task",
            "continued_execution",
            "continued_observation",
            "continued_decision",
        }

        self.assertEqual(set(properties), expected)

    def test_execution_continuation_schema_reuses_public_schemas(self):
        properties = self.schemas["ExecutionContinuationSchema"]["properties"]

        self.assertEqual(
            properties["continued_task"]["anyOf"][0]["$ref"],
            "#/components/schemas/ExecutionCurrentTaskSchema",
        )
        self.assertEqual(
            properties["continued_execution"]["anyOf"][0]["$ref"],
            "#/components/schemas/ExecutionResultSchema",
        )
        self.assertEqual(
            properties["continued_observation"]["anyOf"][0]["$ref"],
            "#/components/schemas/TaskObservationSchema",
        )
        self.assertEqual(
            properties["continued_decision"]["anyOf"][0]["$ref"],
            "#/components/schemas/TaskDecisionSchema",
        )

    def test_clarification_response_exposes_public_fields(self):
        properties = self.schemas["ClarificationResponse"]["properties"]
        expected = {
            "agent",
            "status",
            "question",
            "clarification_token",
            "expires_at",
            "message",
        }

        self.assertEqual(set(properties), expected)

    def test_task_inputs_are_provider_neutral_objects(self):
        for schema_name in ("PlannerTaskSchema", "ExecutionCurrentTaskSchema"):
            with self.subTest(schema=schema_name):
                inputs = self.schemas[schema_name]["properties"]["inputs"]
                self.assertEqual(inputs.get("type"), "object")
                self.assertIs(inputs.get("additionalProperties"), True)

    def test_public_response_schemas_do_not_expose_sensitive_fields(self):
        pending = list(PUBLIC_RESPONSE_VARIANTS)
        visited = set()

        while pending:
            schema_name = pending.pop()
            if schema_name in visited:
                continue
            visited.add(schema_name)
            pending.extend(
                name
                for name in _referenced_schema_names(self.schemas[schema_name])
                if name not in visited
            )

        public_fields = set()
        for schema_name in visited:
            public_fields.update(_property_names(self.schemas[schema_name]))

        forbidden_exact = {
            "plan_id",
            "confirm_token",
            "to_phones",
            "calle_command",
            "api_key",
            "api_keys",
            "credentials",
        }
        forbidden_fragments = ("calle", "adk", "api_key", "credential")
        exposed = {
            field
            for field in public_fields
            if field.lower() in forbidden_exact
            or any(fragment in field.lower() for fragment in forbidden_fragments)
        }

        self.assertEqual(exposed, set())

    def test_chat_request_still_requires_message(self):
        request_schema = self.schemas["ChatRequest"]
        self.assertEqual(request_schema["properties"]["message"]["type"], "string")
        self.assertIn("clarification_token", request_schema["properties"])
        self.assertIn("message", request_schema["required"])
        self.assertNotIn("clarification_token", request_schema["required"])

        request_body = self.chat_post["requestBody"]
        request_ref = request_body["content"]["application/json"]["schema"]["$ref"]
        self.assertEqual(request_ref, "#/components/schemas/ChatRequest")

    def test_openapi_can_be_generated_repeatedly(self):
        original_schema = app.openapi_schema
        generated = []
        try:
            for _ in range(3):
                app.openapi_schema = None
                generated.append(app.openapi())
        finally:
            app.openapi_schema = original_schema

        self.assertEqual(generated[0], generated[1])
        self.assertEqual(generated[1], generated[2])


if __name__ == "__main__":
    unittest.main()
