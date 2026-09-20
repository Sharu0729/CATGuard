import sqlite3


DATABASE_NAME = "database/catguard.db"


def create_database():
    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS social_media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT UNIQUE NOT NULL,
            time_limit INTEGER NOT NULL,
            enabled INTEGER NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_setting(app_name, time_limit, enabled):
    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO social_media
        (app_name, time_limit, enabled)
        VALUES (?, ?, ?)
    """, (
        app_name,
        time_limit,
        enabled
    ))

    connection.commit()
    connection.close()


def get_settings():
    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT app_name, time_limit, enabled
        FROM social_media
    """)

    settings = cursor.fetchall()

    connection.close()

    return settings


# Create database when this file runs
create_database()

print("CATGuard database ready!")