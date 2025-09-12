"""
Migration script to create channels and programmes tables for normalized EPG data storage
This migration adds two new tables to store EPG data in a normalized format instead of JSON
"""
import sqlite3
import os

from migration_utils import get_database_path


def create_channels_and_programmes_tables():
    """
    Create channels and programmes tables for normalized EPG data storage
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

        # Check if channels table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='channels'")
        if cursor.fetchone():
            print("Channels table already exists. Skipping channels table creation.")
        else:
            # Create channels table
            cursor.execute("""
                           CREATE TABLE channels
                           (
                             id               INTEGER PRIMARY KEY AUTOINCREMENT,
                             user_id          TEXT    NOT NULL,
                             server_id        INTEGER NOT NULL,
                             xmltv_id         TEXT    NOT NULL,
                             display_names    TEXT,
                             icons            TEXT,
                             urls             TEXT,
                             date_created     DATETIME DEFAULT CURRENT_TIMESTAMP,
                             date_last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                             FOREIGN KEY (user_id) REFERENCES users (id),
                             FOREIGN KEY (server_id) REFERENCES servers (id),
                             CONSTRAINT uq_channel_user_server_xmltv UNIQUE (user_id, server_id, xmltv_id)
                           )
                           """)

            # Create indexes for channels table
            cursor.execute("CREATE INDEX idx_channels_user_id ON channels(user_id)")
            cursor.execute("CREATE INDEX idx_channels_server_id ON channels(server_id)")
            cursor.execute("CREATE INDEX idx_channels_xmltv_id ON channels(xmltv_id)")
            cursor.execute("CREATE INDEX idx_channels_user_server ON channels(user_id, server_id)")
            print("Channels table created successfully!")

        # Check if programmes table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='programmes'")
        if cursor.fetchone():
            print("Programmes table already exists. Skipping programmes table creation.")
        else:
            # Create programmes table
            cursor.execute("""
                           CREATE TABLE programmes
                           (
                             id               INTEGER PRIMARY KEY AUTOINCREMENT,
                             channel_id       INTEGER NOT NULL,
                             start_time       TEXT    NOT NULL,
                             stop_time        TEXT,
                             pdc_start        TEXT,
                             vps_start        TEXT,
                             showview         TEXT,
                             videoplus        TEXT,
                             clumpidx         TEXT    DEFAULT '0/1',
                             titles           TEXT,
                             sub_titles       TEXT,
                             descriptions     TEXT,
                             credits          TEXT,
                             date             TEXT,
                             categories       TEXT,
                             keywords         TEXT,
                             language         TEXT,
                             orig_language    TEXT,
                             length           TEXT,
                             icons            TEXT,
                             urls             TEXT,
                             countries        TEXT,
                             episode_nums     TEXT,
                             video            TEXT,
                             audio            TEXT,
                             previously_shown TEXT,
                             premiere         TEXT,
                             last_chance      TEXT,
                             new              BOOLEAN DEFAULT 0,
                             subtitles        TEXT,
                             ratings          TEXT,
                             star_ratings     TEXT,
                             reviews          TEXT,
                             images           TEXT,
                             date_created     DATETIME DEFAULT CURRENT_TIMESTAMP,
                             date_last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                             FOREIGN KEY (channel_id) REFERENCES channels (id) ON DELETE CASCADE
                           )
                           """)

            # Create indexes for programmes table
            cursor.execute("CREATE INDEX idx_programmes_channel_id ON programmes(channel_id)")
            cursor.execute("CREATE INDEX idx_programmes_start_time ON programmes(start_time)")
            cursor.execute("CREATE INDEX idx_programmes_stop_time ON programmes(stop_time)")
            cursor.execute("CREATE INDEX idx_programme_channel_start ON programmes(channel_id, start_time)")
            cursor.execute("CREATE INDEX idx_programme_start_stop ON programmes(start_time, stop_time)")
            print("Programmes table created successfully!")

        # Commit transaction
        cursor.execute("COMMIT")
        print("Migration completed successfully!")

        print(f"Migration summary:")
        print(f"- Created channels table with user/server/xmltv_id composite constraint")
        print(f"- Created programmes table with foreign key to channels")
        print(f"- Added indexes for performance optimization")
        print(f"- Stored complex data as JSON text fields for flexibility")
        print(f"- Database: {db_path}")

    except Exception as e:
        cursor.execute("ROLLBACK")
        print(f"Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    create_channels_and_programmes_tables()