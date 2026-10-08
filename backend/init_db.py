"""
Database Initialization and Migration Script.
Verifies connection to local or remote MySQL and ensures all ORM tables are created.
Usage:
    python backend/init_db.py
"""

import sys
import os

# Ensure backend root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from database.connection import get_or_create_engine, init_db, check_db_connection, Base
from models.user import User
from models.review import CodeReview
from models.finding import Finding
from models.suggestion import Suggestion
from app.config import settings

def main():
    print("=" * 60)
    print("AI-Powered Code Review Platform - Database Initialization")
    print("=" * 60)
    print(f"Target Database URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    print(f"Environment: {settings.APP_ENV}")

    eng, session_maker = get_or_create_engine()
    if eng is None:
        print("[ERROR] Failed to configure SQLAlchemy engine.")
        sys.exit(1)

    print("[INFO] Verifying database connectivity...")
    ok, msg = check_db_connection()
    if not ok:
        print(f"[ERROR] Database connection failed: {msg}")
        sys.exit(1)
    print(f"[SUCCESS] {msg}")

    print("[INFO] Applying database schema (creating tables if not exist)...")
    init_db()

    # Verify tables
    from sqlalchemy import inspect
    inspector = inspect(eng)
    tables = inspector.get_table_names()
    print(f"[SUCCESS] Verified existing tables in database: {tables}")

    required_tables = {"users", "code_reviews", "findings", "suggestions"}
    missing = required_tables - set(tables)
    if missing:
        print(f"[WARNING] Missing expected tables: {missing}")
    else:
        print("[SUCCESS] All required tables are present and ready for production traffic.")

if __name__ == "__main__":
    main()
