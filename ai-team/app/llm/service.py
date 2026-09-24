"""Answer generation from retrieved context."""

from logging import Logger

from app.common.constants import NO_RESULTS_FOUND
from app.common.interfaces import BaseLLMService, RetrievalResult
from app.common.logger import get_logger


class LLMService(BaseLLMService):
    """Stub: echoes the retrieved context instead of generating."""

    def __init__(self, logger: Logger | None = None):
        self._logger = logger or get_logger(__name__)

    async def generate(
        self,
        query: str,
        context: list[RetrievalResult],
        history: list[dict] | None = None,
    ) -> str:
        # TODO(#2): build a prompt and call the model
        self._logger.warning("LLMService is a stub — returning raw context")

        if not context:
            return NO_RESULTS_FOUND
        return "\n\n".join(r.content for r in context)
