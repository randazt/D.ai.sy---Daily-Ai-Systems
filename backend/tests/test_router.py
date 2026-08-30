"""Regression tests for D.AI.SY agent routing.

These tests protect the human-authority boundary:

Natural-language discussion about starting, launching, running, finishing,
or completing something must not itself authorize agentic execution.

Execution requires an explicit execution command.
"""

import unittest

from app.orchestration.router import AgentRouter


class AgentRouterTests(unittest.TestCase):
    def setUp(self):
        self.router = AgentRouter()

    def test_empty_message_routes_to_conversation(self):
        self.assertEqual(self.router.route(""), "conversation")

    def test_general_message_routes_to_conversation(self):
        self.assertEqual(
            self.router.route("I'm feeling stuck and I need help thinking this through."),
            "conversation",
        )

    def test_build_intent_routes_to_planner(self):
        self.assertEqual(
            self.router.route("Help me build a project plan."),
            "planner",
        )

    def test_explicit_execute_command_routes_to_execution(self):
        self.assertEqual(self.router.route("execute"), "execution")

    def test_slash_execute_command_routes_to_execution(self):
        self.assertEqual(self.router.route("/execute"), "execution")

    def test_explicit_run_command_routes_to_execution(self):
        self.assertEqual(self.router.route("run"), "execution")

    def test_uncertainty_about_starting_does_not_execute(self):
        self.assertNotEqual(
            self.router.route(
                "I have an idea for something I really want to build, "
                "but it's still all over the place in my head. "
                "I know what I care about, but I don't know how to turn "
                "it into something I can actually start."
            ),
            "execution",
        )

    def test_help_me_start_does_not_execute(self):
        self.assertNotEqual(
            self.router.route("Help me start a business."),
            "execution",
        )

    def test_launching_an_idea_does_not_execute(self):
        self.assertNotEqual(
            self.router.route("I want to launch an idea but I don't know where to begin."),
            "execution",
        )

    def test_question_about_finishing_does_not_execute(self):
        self.assertNotEqual(
            self.router.route("How do I finish this project?"),
            "execution",
        )

    def test_question_about_running_something_does_not_execute(self):
        self.assertNotEqual(
            self.router.route("Can you help me understand how to run this workflow?"),
            "execution",
        )

    def test_completion_language_does_not_execute(self):
        self.assertNotEqual(
            self.router.route("I'm overwhelmed trying to complete this goal."),
            "execution",
        )

    def test_execute_inside_natural_language_does_not_grant_authority(self):
        self.assertNotEqual(
            self.router.route(
                "I'm not sure whether I'm ready to execute this plan yet."
            ),
            "execution",
        )


if __name__ == "__main__":
    unittest.main()