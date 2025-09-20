import pytest
from datetime import datetime, timezone

from app.models.server import Server
from tests.factories import create_test_server, create_test_user


class TestServerModel:
    """Test cases for the Server model."""

    @pytest.mark.unit
    def test_server_creation(self, test_session):
        """Test basic server creation."""
        user = create_test_user(test_session)
        server = create_test_server(
            test_session,
            name="Test Server",
            url="http://example.com:8080",
            username="testuser",
            password="testpass",
            owner=user
        )

        assert server.id is not None
        assert server.name == "Test Server"
        assert server.url == "http://example.com:8080"
        assert server.username == "testuser"
        assert server.password == "testpass"
        assert server.owner == user
        assert isinstance(server.date_created, datetime)
        assert isinstance(server.date_last_updated, datetime)

    @pytest.mark.unit
    def test_server_owner_relationship(self, test_session):
        """Test the relationship between servers and users."""
        user1 = create_test_user(test_session, email="user1@example.com")
        user2 = create_test_user(test_session, email="user2@example.com")

        server1 = create_test_server(test_session, owner=user1, name="User1 Server")
        server2 = create_test_server(test_session, owner=user2, name="User2 Server")

        test_session.commit()

        # Each server should belong to the correct user
        assert server1.owner == user1
        assert server2.owner == user2

        # Users should have their respective servers
        assert server1 in user1.servers
        assert server2 in user2.servers
        assert server1 not in user2.servers
        assert server2 not in user1.servers

    @pytest.mark.unit
    def test_server_optional_fields(self, test_session):
        """Test that optional fields can be None."""
        user = create_test_user(test_session)
        server = create_test_server(
            test_session,
            owner=user,
            epg_url=None
        )

        assert server.epg_url is None
        assert server.owner is not None

    @pytest.mark.unit
    def test_server_channels_relationship(self, test_session):
        """Test the relationship between servers and channels."""
        from tests.factories import create_test_channel

        user = create_test_user(test_session)
        server = create_test_server(test_session, owner=user)

        channel1 = create_test_channel(test_session, server=server, user=user, 
                                     display_names='["Channel 1"]')
        channel2 = create_test_channel(test_session, server=server, user=user,
                                     display_names='["Channel 2"]')

        test_session.commit()

        # Server should have access to its channels
        assert len(server.channels) == 2
        assert channel1 in server.channels
        assert channel2 in server.channels
