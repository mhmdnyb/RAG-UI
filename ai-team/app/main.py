from app.retrieval.sql_pipeline.engine import build_sql_query_engine

if __name__ == "__main__":
    query_engine = build_sql_query_engine()
    response = query_engine.query(
        "چه درس‌هایی روز یکشنبه کلاس دارند؟"
    )  # "which courses have class on Sunday?"
    print(response)
