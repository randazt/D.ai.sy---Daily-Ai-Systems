"""
Agent routing for D.AI.S.Y.

Determines which agent should handle an incoming request.

Routing follows D.AI.SY's human-authority boundary:

1. Explicit agent commands may directly select an agent.
2. Natural-language planning intent may route to the planner.
3. Natural-language action words do not authorize execution.
4. Execution requires an explicit execution command.
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

        # Execution is an authority boundary.
        #
        # These exact commands represent an explicit request to
        # enter the execution path. Merely mentioning words such
        # as "run", "execute", "start", "launch", "complete", or
        # "finish" inside normal language does not authorize action.
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
        # Planner intent
        # ----------------------------------------------------
        #
        # Planning language may identify that the user wants help
        # shaping work, but ChatService still owns the clarification
        # gate before the planner is allowed to proceed.
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
        #
        # Ambiguous or general human language remains conversation.
        # D.AI.SY should understand the person's intent before
        # escalating toward structured planning or authorized action.
        return "conversation"


router = AgentRouter()