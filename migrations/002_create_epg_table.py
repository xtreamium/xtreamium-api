"""
Migration script to create EPG table for storing parsed EPG data
This migration adds a new table to store EPG programs with composite key of user_id and server_id
"""
import sqlite3
import os

from migration_utils import get_database_path


def create_epg_table():
    """
    Create EPG table for storing parsed EPG data
    """
    try:
        db_path = get_database_path()
    except (ImportError, ValueError) as e:
        print(f"Migration failed: {e}")
        return

    print(f"Using database: {db_path}")

    if not os.path.exists(db_path):
        print("Database file not found. Please run the application first to create the database.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")

        # Check if epg table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='epg'")
        if cursor.fetchone():
            print("EPG table already exists. Skipping migration.")
            cursor.execute("ROLLBACK")
            return

        # Create EPG table
        cursor.execute("""
                       CREATE TABLE epg
                       (
                         user_id       TEXT    NOT NULL,
                         server_id     INTEGER NOT NULL,
                         programs_data TEXT    NOT NULL,
                         last_updated  DATETIME DEFAULT CURRENT_TIMESTAMP,
                         program_count INTEGER  DEFAULT 0,
                         PRIMARY KEY (user_id, server_id),
                         FOREIGN KEY (user_id) REFERENCES users (id),
                         FOREIGN KEY (server_id) REFERENCES servers (id)
                       )
                       """)

        # Create indexes for better performance
        cursor.execute("CREATE INDEX idx_epg_user_id ON epg(user_id)")
        cursor.execute("CREATE INDEX idx_epg_server_id ON epg(server_id)")
        cursor.execute("CREATE INDEX idx_epg_last_updated ON epg(last_updated)")

        # Commit transaction
        cursor.execute("COMMIT")
        print("EPG table created successfully!")

        print(f"Migration summary:")
        print(f"- Created EPG table with composite primary key (user_id, server_id)")
        print(f"- Added indexes for performance optimization")
        print(f"- Database: {db_path}")

    except Exception as e:
        cursor.execute("ROLLBACK")
        print(f"Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    create_epg_table()
