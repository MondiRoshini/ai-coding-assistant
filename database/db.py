import sqlite3

DB_NAME = "coding_tutor.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_settings (
        id INTEGER PRIMARY KEY,
        skill_level TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_skill_level(level):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM user_settings")

    cursor.execute(
        """
        INSERT INTO user_settings(skill_level)
        VALUES(?)
        """,
        (level,)
    )

    conn.commit()
    conn.close()


def load_skill_level():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT skill_level
        FROM user_settings
        LIMIT 1
        """
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return "Beginner"