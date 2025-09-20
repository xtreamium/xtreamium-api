import pytest
from datetime import datetime

from app.models.channel import Channel
from tests.factories import create_test_channel, create_test_user, create_test_server


class TestChannelModel:
    """Test cases for the Channel model."""

    @pytest.mark.unit
    def test_channel_creation(self, test_session):
        """Test basic channel creation."""
        user = create_test_user(test_session)
        server = create_test_server(test_session, owner=user)

        channel = create_test_channel(
            test_session,
            xmltv_id="test.channel",
            display_names='["Test Channel"]',
            user=user,
            server=server
        )

        assert channel.id is not None
        assert channel.xmltv_id == "test.channel"
        assert channel.display_names == '["Test Channel"]'
        assert channel.user == user
        assert channel.server == server

    @pytest.mark.unit
    def test_channel_json_fields(self, test_session):
        """Test channel JSON field storage."""
        user = create_test_user(test_session)
        server = create_test_server(test_session, owner=user)

        channel = create_test_channel(
            test_session,
            xmltv_id="json.test",
            display_names='["JSON Test Channel", "Alternative Name"]',
            icons='[{"src": "http://example.com/icon.png", "width": "32", "height": "32"}]',
            urls='["http://example.com", "http://backup.com"]',
            user=user,
            server=server
        )

        # Verify JSON fields are stored correctly
        assert '"JSON Test Channel"' in channel.display_names
        assert '"src": "http://example.com/icon.png"' in channel.icons
        assert '"http://example.com"' in channel.urls

    @pytest.mark.unit
    def test_channel_unique_constraint(self, test_session):
        """Test unique constraint on user_id, server_id, xmltv_id."""
        user = create_test_user(test_session)
        server = create_test_server(test_session, owner=user)

        # Create first channel
        channel1 = create_test_channel(
            test_session,
            user=user,
            server=server,
            xmltv_id="unique.channel"
        )
        test_session.commit()

        # Attempt to create duplicate should fail
        with pytest.raises(Exception):
            channel2 = create_test_channel(
                test_session,
                user=user,
                server=server,
                xmltv_id="unique.channel"
            )
            test_session.commit()

    @pytest.mark.unit
    def test_channel_relationships(self, test_session):
        """Test channel relationships with user and server."""
        user1 = create_test_user(test_session, email="user1@example.com")
        user2 = create_test_user(test_session, email="user2@example.com")
        server1 = create_test_server(test_session, owner=user1, name="Server 1")
        server2 = create_test_server(test_session, owner=user2, name="Server 2")

        channel1 = create_test_channel(test_session, user=user1, server=server1)
        channel2 = create_test_channel(test_session, user=user2, server=server2)

        test_session.commit()

        # Channels should belong to correct users and servers
        assert channel1.user == user1
        assert channel1.server == server1
        assert channel2.user == user2
        assert channel2.server == server2

        # Users should have their channels
        assert channel1 in user1.channels
        assert channel2 in user2.channels
