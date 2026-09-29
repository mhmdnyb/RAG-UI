"""
Conversation history.

Not wired into the pipeline yet — see ARCHITECTURE.md for the open
question of where history should come from. Do not build on this.
"""

from logging import Logger

from app.common.interfaces import BaseChatHistory
from app.common.logger import get_logger


class ChatHistoryService(BaseChatHistory):
    """Stub: in-memory, lost on restart."""

    def __init__(self, logger: Logger | None = None):
        self._logger = logger or get_logger(__name__)
        self._store: dict[str, list[dict]] = {}

    async def get_history(self, conversation_id: str) -> list[dict]:
        history = self._store.get(conversation_id, [])
        self._logger.info(
            f"Retrieved {len(history)} turns for conversation {conversation_id}"
        )
        return history

    async def save_turn(self, conversation_id: str, question: str, answer: str) -> None:
        turns = self._store.setdefault(conversation_id, [])
        turns.append({"role": "user", "content": question})
        turns.append({"role": "assistant", "content": answer})
        self._logger.info(f"Saved turn for conversation {conversation_id}")
