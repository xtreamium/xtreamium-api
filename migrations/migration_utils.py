"""
Migration utilities module
Shared helper functions for database migrations
"""
import os
import sys


def get_database_path():
  """
  Get the database path from the app configuration
  Returns the absolute path to the database file
  """
  # First try to import DATABASE_URL from app.database
  project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  if project_root not in sys.path:
    sys.path.insert(0, project_root)  # Insert at beginning to prioritize local app

  try:
    from app.database import DATABASE_URL

    # Parse DATABASE_URL to get the actual database file path
    if DATABASE_URL.startswith("sqlite:///"):
      # Remove sqlite:/// prefix to get absolute path
      db_path = DATABASE_URL[10:]  # Remove "sqlite:///"
      return db_path
    else:
      raise ValueError(f"This migration only supports SQLite databases. Found: {DATABASE_URL}")

  except ImportError as e:
    # Fallback: Use the same path calculation as the updated database.py
    print(f"Warning: Could not import DATABASE_URL ({e}), using fallback path calculation")
    app_dir = os.path.join(project_root, "app")
    db_path = os.path.join(app_dir, "xtreamium.db")
    print(f"Fallback database path: {db_path}")
    return db_path


def connect_to_database():
  """
  Connect to the application database using the configured path
  Returns a sqlite3 connection object
  """
  import sqlite3

  db_path = get_database_path()
  print(f"Using database: {db_path}")

  if not os.path.exists(db_path):
    raise FileNotFoundError(f"Database file not found: {db_path}")

  return sqlite3.connect(db_path)
