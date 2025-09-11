"""
Migration script to convert User.id from integer to UUID
This script handles the migration of existing data while changing the schema
"""
import uuid
import sqlite3
import os
import sys

# Add the parent directory to sys.path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import DATABASE_URL

def migrate_to_uuid():
    """
    Migrate User table from integer ID to UUID
    """
    # Parse DATABASE_URL to get the actual database file path
    if DATABASE_URL.startswith("sqlite:///"):
        # Remove sqlite:/// prefix to get absolute path
        db_path = DATABASE_URL[10:]  # Remove "sqlite:///"
    else:
        print(f"This migration only supports SQLite databases. Found: {DATABASE_URL}")
        return

    print(f"Using database: {db_path}")

    if not os.path.exists(db_path):
        print("Database file not found, creating new schema with UUID...")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Users table not found. Database may be empty or not initialized.")
            cursor.execute("ROLLBACK")
            return

        # Create a mapping table for old ID to new UUID
        cursor.execute("""
            CREATE TEMPORARY TABLE user_id_mapping (
                old_id INTEGER,
                new_id TEXT
            )
        """)
        
        # Get all existing users and create UUID mappings
        cursor.execute("SELECT id FROM users")
        existing_users = cursor.fetchall()
        
        uuid_mappings = []
        for (old_id,) in existing_users:
            new_uuid = str(uuid.uuid4())
            uuid_mappings.append((old_id, new_uuid))
            cursor.execute("INSERT INTO user_id_mapping (old_id, new_id) VALUES (?, ?)", 
                         (old_id, new_uuid))
        
        print(f"Created UUID mappings for {len(uuid_mappings)} users")
        
        # Create new users table with UUID
        cursor.execute("""
            CREATE TABLE users_new (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
                date_last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Copy data from old table to new table with UUID mappings
        cursor.execute("""
            INSERT INTO users_new (id, email, hashed_password, date_created, date_last_updated)
            SELECT m.new_id, u.email, u.hashed_password, u.date_created, u.date_last_updated
            FROM users u
            JOIN user_id_mapping m ON u.id = m.old_id
        """)
        
        # Check if servers table exists before migrating it
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='servers'")
        if cursor.fetchone():
            # Update servers table to use new UUID foreign keys
            cursor.execute("""
                CREATE TABLE servers_new (
                    id INTEGER PRIMARY KEY,
                    owner_id TEXT NOT NULL,
                    name TEXT UNIQUE NOT NULL,
                    url TEXT,
                    username TEXT,
                    password TEXT,
                    epg_url TEXT,
                    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
                    date_last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_id) REFERENCES users_new (id)
                )
            """)

            # Copy servers data with updated foreign keys
            cursor.execute("""
                INSERT INTO servers_new (id, owner_id, name, url, username, password, epg_url, date_created, date_last_updated)
                SELECT s.id, m.new_id, s.name, s.url, s.username, s.password, s.epg_url, s.date_created, s.date_last_updated
                FROM servers s
                JOIN user_id_mapping m ON s.owner_id = m.old_id
            """)

            # Drop old servers table
            cursor.execute("DROP TABLE servers")
            cursor.execute("ALTER TABLE servers_new RENAME TO servers")
            cursor.execute("CREATE INDEX idx_servers_owner_id ON servers(owner_id)")
            cursor.execute("CREATE INDEX idx_servers_name ON servers(name)")

        # Drop old users table
        cursor.execute("DROP TABLE users")

        # Rename new users table
        cursor.execute("ALTER TABLE users_new RENAME TO users")

        # Create indexes
        cursor.execute("CREATE INDEX idx_users_email ON users(email)")

        # Commit transaction
        cursor.execute("COMMIT")
        print("Migration completed successfully!")
        
        # Print summary
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM servers")
        server_count = cursor.fetchone()[0] if cursor.fetchone() else 0

        print(f"Migration summary:")
        print(f"- {user_count} users migrated to UUID")
        print(f"- {server_count} servers updated with new foreign keys")
        print(f"- Database: {db_path}")

    except Exception as e:
        cursor.execute("ROLLBACK")
        print(f"Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_to_uuid()
