"""
Base interface for all D.AI.SY agents.

Every concrete agent should inherit from BaseAgent and implement
the required asynchronous interface.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """
    Base interface for all D.AI.SY agents.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the agent."""
        pass

    @abstractmethod
    async def run(self, request: Any) -> Any:
        """
        Execute the agent.

        Args:
            request: Structured input for the agent.

        Returns:
            Agent-specific response.
        """
        pass