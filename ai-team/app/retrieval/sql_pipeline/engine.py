# app/retrieval/sql_pipeline/engine.py

import os
from sqlalchemy import create_engine
from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from app.common.config import settings
from .schema import TABLE_SCHEMA_DESCRIPTION


def build_sql_query_engine():
    db_url = os.getenv("DATABASE_URL") or settings.database_url
    engine = create_engine(db_url)
    sql_database = SQLDatabase(engine, include_tables=["classes"])

    query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["classes"],
        context_str_prefix=TABLE_SCHEMA_DESCRIPTION,
    )
    return query_engine
