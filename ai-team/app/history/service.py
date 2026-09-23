"""
Chat History Service — persists and retrieves conversation turns.

Owner: Dev 6

TODO: Implement actual database-backed conversation storage.
"""

from logging import Logger

from common.interfaces import BaseChatHistory
from common.logger import get_logger


class ChatHistoryService(BaseChatHistory):
    """
    Manages conversation history per conversation ID.

    This is a STUB — replace with actual DB-backed implementation.
    Currently uses an in-memory dictionary (lost on restart).
    """

    def __init__(self, logger: Logger | None = None):
        self._logger = logger or get_logger(__name__)
        self._store: dict[str, list[dict]] = {}

    async def get_history(self, conversation_id: str) -> list[dict]:
        """
        TODO: Replace with database query.

        Current behavior: returns from in-memory store.
        """
        history = self._store.get(conversation_id, [])
        self._logger.info(
            f"Retrieved {len(history)} turns for conversation {conversation_id}"
        )
        return history

    async def save_turn(
        self, conversation_id: str, question: str, answer: str
    ) -> None:
        """
        TODO: Replace with database INSERT.

        Current behavior: appends to in-memory store.
        """
        if conversation_id not in self._store:
            self._store[conversation_id] = []

        self._store[conversation_id].append(
            {"role": "user", "content": question}
        )
        self._store[conversation_id].append(
            {"role": "assistant", "content": answer}
        )
        self._logger.info(
            f"Saved turn for conversation {conversation_id}"
        )
