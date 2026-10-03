import os
from sqlalchemy import create_engine
from llama_index.core import SQLDatabase, Settings
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.embeddings.mock_embed_model import MockEmbedding
from llama_index.core.base.llms.types import LLMMetadata
from app.common.config import settings
from .schema import TABLE_SCHEMA_DESCRIPTION


def build_sql_query_engine(llm=None):
    db_url = os.getenv("DATABASE_URL") or settings.database_url
    engine = create_engine(db_url)
    sql_database = SQLDatabase(engine, include_tables=["classes"])

    if llm is None and settings.resolved_llm_api_key:
        try:
            from llama_index.llms.openai import OpenAI

            class RobustOpenAI(OpenAI):
                @property
                def metadata(self) -> LLMMetadata:
                    return LLMMetadata(
                        context_window=128000,
                        num_output=self.max_tokens or 4096,
                        is_chat_model=True,
                        is_function_calling_model=False,
                        model_name=self.model,
                    )

            llm = RobustOpenAI(
                model=settings.resolved_llm_model,
                api_key=settings.resolved_llm_api_key,
                api_base=settings.resolved_llm_base_url,
            )
        except Exception:
            llm = None

    try:
        Settings.embed_model = MockEmbedding(embed_dim=1536)
    except Exception:
        pass

    kwargs = {
        "sql_database": sql_database,
        "tables": ["classes"],
        "context_str_prefix": TABLE_SCHEMA_DESCRIPTION,
    }
    if llm is not None:
        kwargs["llm"] = llm

    query_engine = NLSQLTableQueryEngine(**kwargs)
    return query_engine
