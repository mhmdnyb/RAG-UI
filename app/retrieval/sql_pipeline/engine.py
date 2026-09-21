# app/retrieval/sql_pipeline/engine.py

import os
from sqlalchemy import create_engine
from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from .schema import TABLE_SCHEMA_DESCRIPTION

def build_sql_query_engine():
    engine = create_engine(os.environ["DATABASE_URL"])
    sql_database = SQLDatabase(engine, include_tables=["classes"])

    query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["classes"],
        context_str_prefix=TABLE_SCHEMA_DESCRIPTION,
    )
    return query_engine