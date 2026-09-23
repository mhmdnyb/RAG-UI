"""
LLM Service — generates natural-language answers from retrieved context.

Owner: Dev 4

TODO: Implement actual LLM API calls (OpenAI, local model, etc.).
"""

from logging import Logger

from common.interfaces import BaseLLMService, RetrievalResult
from common.exceptions import LLMError
from common.logger import get_logger


class LLMService(BaseLLMService):
    """
    Generates answers by sending the user query + retrieved context
    to a large language model.

    This is a STUB — replace with actual implementation.
    """

    def __init__(self, logger: Logger | None = None):
        self._logger = logger or get_logger(__name__)

    async def generate(
        self,
        query: str,
        context: list[RetrievalResult],
        history: list[dict] | None = None,
    ) -> str:
        """
        TODO: Implement LLM generation.

        Expected flow:
        1. Build a prompt from query, context, and history
        2. Call the LLM API
        3. Parse and return the response text

        Current behavior: returns the raw context content as-is.
        """
        self._logger.warning("LLMService is a stub — returning raw context")

        if not context:
            return "متأسفانه اطلاعاتی یافت نشد."  # "No information found"

        # Stub: concatenate context content as the "answer"
        combined = "\n\n".join(r.content for r in context)
        return combined
