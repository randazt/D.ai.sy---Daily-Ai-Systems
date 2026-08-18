"""
Agent routing for D.AI.S.Y.

Determines which agent should handle an incoming request.
Supports both:

1. Explicit agent selection
2. Natural-language intent detection
"""


class AgentRouter:
    """Routes incoming requests to the appropriate agent."""

    def route(self, message: str) -> str:
        if not message:
            return "conversation"

        text = message.strip().lower()

        # ----------------------------------------------------
        # Explicit agent commands
        # ----------------------------------------------------
        if text in {
            "planner",
            "/planner",
            "/plan",
            "plan",
        }:
            return "planner"

        if text in {
            "execution",
            "/execution",
            "/execute",
            "execute",
            "run",
        }:
            return "execution"

        if text in {
            "conversation",
            "/conversation",
            "chat",
            "/chat",
        }:
            return "conversation"

        # ----------------------------------------------------
        # Execution intent
        #
        # Execution is evaluated before planning because an
        # action verb such as "execute" or "run" should take
        # precedence over nouns such as "project".
        # ----------------------------------------------------
        execution_words = [
            "run",
            "execute",
            "start",
            "launch",
            "deploy",
            "complete",
            "finish",
        ]

        if any(word in text for word in execution_words):
            return "execution"

        # ----------------------------------------------------
        # Planner intent
        # ----------------------------------------------------
        planner_words = [
            "build",
            "create",
            "design",
            "develop",
            "make",
            "plan",
            "roadmap",
            "architecture",
            "project",
            "strategy",
        ]

        if any(word in text for word in planner_words):
            return "planner"

        # ----------------------------------------------------
        # Default
        # ----------------------------------------------------
        return "conversation"


router = AgentRouter()