import os
import pandas as pd
import psycopg2

CSV_PATH = "data/classes.csv"

BOOL_COLUMNS = ["has_theory", "has_practical", "has_exercise", "has_exam"]

def to_bool(value):
    if pd.isna(value):
        return None
    return str(value).strip().upper() == "TRUE"

def main():
    df = pd.read_csv(CSV_PATH, sep=",", encoding="utf-8-sig")

    for col in BOOL_COLUMNS:
        df[col] = df[col].apply(to_bool)

    df = df.where(pd.notnull(df), None)

    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS classes;")  # schema changed, start fresh

    cur.execute("""
        CREATE TABLE classes (
            id SERIAL PRIMARY KEY,
            course_code TEXT,
            group_number TEXT,
            course_name TEXT,
            total_units INTEGER,
            practical_units INTEGER,
            capacity INTEGER,
            waiting_list INTEGER,
            teacher_name TEXT,
            has_theory BOOLEAN,
            theory_day TEXT,
            theory_start_time INTEGER,
            theory_end_time INTEGER,
            theory_location TEXT,
            has_practical BOOLEAN,
            practical_day TEXT,
            practical_start_time INTEGER,
            practical_end_time INTEGER,
            practical_location TEXT,
            has_exercise BOOLEAN,
            exercise_day TEXT,
            exercise_start_time INTEGER,
            exercise_end_time INTEGER,
            exercise_location TEXT,
            has_exam BOOLEAN,
            exam_date TEXT,
            exam_start_time TEXT,
            exam_end_time TEXT,
            description TEXT,
            emergency_drop_allowed BOOLEAN
        );
    """)

    columns = list(df.columns)
    placeholders = ", ".join(["%s"] * len(columns))
    insert_sql = f"INSERT INTO classes ({', '.join(columns)}) VALUES ({placeholders})"

    for row in df.itertuples(index=False, name=None):
        cur.execute(insert_sql, row)

    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(df)} rows into classes table.")

if __name__ == "__main__":
    main()