#!/usr/bin/env python3
"""
Test script to verify the initial user creation functionality.
"""
import os
import tempfile
import sys

# Add the app directory to the path
sys.path.insert(0, '/srv/dev/xtreamium/xtreamium-api')

from app import database
from app.models.user import User
from app.services.initial_setup import check_and_create_initial_user


def test_initial_user_creation():
    """Test the initial user creation functionality."""
    print("🧪 Testing initial user creation functionality...")
    
    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    # Override the database URL for testing
    original_db_url = os.environ.get('DATABASE_URL')
    os.environ['DATABASE_URL'] = f'sqlite:///{temp_db_path}'
    
    try:
        # Recreate the engine with the test database
        import sqlalchemy as sa
        import sqlalchemy.orm as orm
        
        engine = sa.create_engine(f'sqlite:///{temp_db_path}')
        SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create all tables
        database.Base.metadata.create_all(bind=engine)
        
        print("📋 Test 1: No environment variables set (should fail)")
        # Remove env vars if they exist
        if 'INITIAL_USER_EMAIL' in os.environ:
            del os.environ['INITIAL_USER_EMAIL']
        if 'INITIAL_USER_PASSWORD' in os.environ:
            del os.environ['INITIAL_USER_PASSWORD']
        
        db = SessionLocal()
        try:
            check_and_create_initial_user(db)
            print("❌ Test 1 FAILED: Should have thrown an error!")
        except RuntimeError as e:
            print(f"✅ Test 1 PASSED: Correctly failed with: {e}")
        finally:
            db.close()
        
        print("\n📋 Test 2: Environment variables set (should succeed)")
        # Set the environment variables
        os.environ['INITIAL_USER_EMAIL'] = 'admin@example.com'
        os.environ['INITIAL_USER_PASSWORD'] = 'secure_password123'
        
        db = SessionLocal()
        try:
            check_and_create_initial_user(db)
            
            # Check if user was created
            user = db.query(User).filter(User.email == 'admin@example.com').first()
            if user:
                print(f"✅ Test 2 PASSED: User created with ID: {user.id}")
            else:
                print("❌ Test 2 FAILED: User was not created")
        except Exception as e:
            print(f"❌ Test 2 FAILED: Unexpected error: {e}")
        finally:
            db.close()
        
        print("\n📋 Test 3: User already exists (should skip)")
        db = SessionLocal()
        try:
            initial_count = db.query(User).count()
            check_and_create_initial_user(db)
            final_count = db.query(User).count()
            
            if initial_count == final_count:
                print("✅ Test 3 PASSED: Correctly skipped user creation when user already exists")
            else:
                print("❌ Test 3 FAILED: Should have skipped user creation")
        except Exception as e:
            print(f"❌ Test 3 FAILED: Unexpected error: {e}")
        finally:
            db.close()
    
    finally:
        # Cleanup
        if original_db_url:
            os.environ['DATABASE_URL'] = original_db_url
        elif 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']
        
        # Clean up test environment variables
        if 'INITIAL_USER_EMAIL' in os.environ:
            del os.environ['INITIAL_USER_EMAIL']
        if 'INITIAL_USER_PASSWORD' in os.environ:
            del os.environ['INITIAL_USER_PASSWORD']
        
        # Remove the temporary database file
        try:
            os.unlink(temp_db_path)
        except:
            pass
    
    print("\n🎉 All tests completed!")


if __name__ == '__main__':
    test_initial_user_creation()