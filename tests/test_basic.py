import pytest
from app.models.user import User
from app.models.server import Server


class TestBasicModels:
    """Basic tests to verify the test infrastructure works."""

    @pytest.mark.unit
    def test_user_model_basic(self, test_session):
        """Test basic user model functionality."""
        from app.services.data.user_data_services import ph

        # Create user directly without factory to avoid field issues
        test_password = "secret"
        hashed_password = ph.hash(test_password)

        user = User(
            id="test-user-123",
            email="test@example.com",
            hashed_password=hashed_password
        )
        test_session.add(user)
        test_session.commit()

        # Verify user was created
        assert user.id == "test-user-123"
        assert user.email == "test@example.com"

        # Test password verification using argon2
        try:
            ph.verify(user.hashed_password, "secret")
            password_valid = True
        except Exception:
            password_valid = False
        assert password_valid is True

        try:
            ph.verify(user.hashed_password, "wrong")
            wrong_password_valid = True
        except Exception:
            wrong_password_valid = False
        assert wrong_password_valid is False

    @pytest.mark.unit
    def test_server_model_basic(self, test_session):
        """Test basic server model functionality."""
        # Create user first
        user = User(
            id="test-user-456",
            email="server@example.com",
            hashed_password="$2b$12$bKbjutBQu8g./K50qXPmku..De7DVllt1yBMuFhbQWIZ/tjms.h7m"
        )
        test_session.add(user)
        test_session.flush()  # Get the user ID

        # Create server
        server = Server(
            id="test-server-789",
            name="Test Server",
            url="http://example.com:8080",
            username="testuser",
            password="testpass",
            owner_id=user.id
        )
        test_session.add(server)
        test_session.commit()

        # Verify server was created with relationship
        assert server.name == "Test Server"
        assert server.owner_id == user.id
        assert len(user.servers) == 1
        assert user.servers[0] == server
