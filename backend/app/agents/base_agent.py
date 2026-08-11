"""
Base interface for all D.AI.SY agents.

Every concrete agent should inherit from BaseAgent and implement
the common execution interface.
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
    def run(self, request: Any) -> Any:
        """
        Execute the agent and return its response.

        Args:
            request: Structured input for the agent.

        Returns:
            Agent-specific response.
        """
        pass