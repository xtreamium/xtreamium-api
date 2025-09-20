import pytest
from datetime import datetime, timezone

from app.models.user import User
from tests.factories import create_test_user


class TestUserModel:
    """Test cases for the User model."""

    @pytest.mark.unit
    def test_user_creation(self, test_session):
        """Test basic user creation."""
        user = create_test_user(test_session, email="test@example.com")

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.hashed_password is not None
        assert isinstance(user.date_created, datetime)
        assert isinstance(user.date_last_updated, datetime)

    @pytest.mark.unit
    def test_user_password_verification(self, test_session):
        """Test password verification functionality."""
        # Create user with a known hashed password
        import passlib.hash as passlib_hash

        test_password = "secret123"
        hashed_password = passlib_hash.bcrypt.hash(test_password)

        user = create_test_user(
            test_session,
            hashed_password=hashed_password,
        )

        # Should verify correct password
        assert user.verify_password(test_password) is True

        # Should reject incorrect password
        assert user.verify_password("wrong_password") is False

    @pytest.mark.unit
    def test_user_email_uniqueness(self, test_session):
        """Test that user emails must be unique."""
        email = "unique@example.com"

        # Create first user
        user1 = create_test_user(test_session, email=email)
        test_session.commit()

        # Attempt to create second user with same email should fail
        with pytest.raises(Exception):  # SQLAlchemy will raise an integrity error
            user2 = create_test_user(test_session, email=email)
            test_session.commit()

    @pytest.mark.unit
    def test_user_servers_relationship(self, test_session):
        """Test the relationship between users and servers."""
        from tests.factories import create_test_server

        user = create_test_user(test_session)
        server1 = create_test_server(test_session, owner=user, name="Server 1")
        server2 = create_test_server(test_session, owner=user, name="Server 2")

        test_session.commit()

        # User should have access to their servers
        assert len(user.servers) == 2
        assert server1 in user.servers
        assert server2 in user.servers

        # Servers should reference the correct owner
        assert server1.owner == user
        assert server2.owner == user

    @pytest.mark.unit
    def test_user_config_class(self, test_session):
        """Test that the User model config is properly set."""
        user = create_test_user(test_session)

        # Should have from_attributes = True for Pydantic compatibility
        assert hasattr(user, "Config")
        assert user.Config.from_attributes is True
