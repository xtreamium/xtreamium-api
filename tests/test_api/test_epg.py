import pytest
from fastapi import status
from datetime import datetime, timezone
from tests.factories import create_test_user, create_test_server, create_test_epg, create_test_programme, create_test_channel


class TestEPGAPI:
    """Test cases for EPG (Electronic Program Guide) endpoints."""

    @pytest.mark.epg
    def test_get_epg_data(self, client, test_session):
        """Test retrieving EPG data."""
        user = create_test_user(test_session)
        server = create_test_server(test_session, owner=user)
        epg = create_test_epg(test_session, user=user, server=server)
        test_session.commit()

        # Without authentication, should return 401
        response = client.get("/api/v1/epg")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.epg
    def test_refresh_epg_data(self, client, test_session):
        """Test triggering EPG data refresh."""
        response = client.post("/api/v1/epg/refresh")

        # Without authentication, should return 401
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.epg
    def test_get_epg_for_channel(self, client, test_session):
        """Test getting EPG data for a specific channel."""
        user = create_test_user(test_session)
        server = create_test_server(test_session, owner=user)
        channel = create_test_channel(test_session, user=user, server=server)

        # Create EPG and programme data
        epg = create_test_epg(test_session, user=user, server=server)
        programme = create_test_programme(test_session, channel=channel)
        test_session.commit()

        response = client.get("/api/v1/epg/channel/test.channel")

        # Without authentication, should return 401
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestEPGModels:
    """Test cases for EPG and Programme models."""

    @pytest.mark.unit
    def test_epg_creation(self, test_session):
        """Test EPG model creation."""
        user = create_test_user(test_session)
        server = create_test_server(test_session, owner=user)

        epg = create_test_epg(
            test_session,
            user=user,
            server=server,
            programs_data='{"programs": [{"title": "Test Program"}]}'
        )

        assert epg.user == user
        assert epg.server == server
        assert epg.programs_data == '{"programs": [{"title": "Test Program"}]}'
        assert isinstance(epg.last_updated, datetime)
        assert epg.program_count >= 0

    @pytest.mark.unit
    def test_programme_creation(self, test_session):
        """Test Programme model creation."""
        user = create_test_user(test_session)
        server = create_test_server(test_session, owner=user)
        channel = create_test_channel(test_session, user=user, server=server)
        
        programme = create_test_programme(
            test_session,
            channel=channel,
            start_time="20230917120000",
            stop_time="20230917130000"
        )

        assert programme.id is not None
        assert programme.channel == channel
        assert programme.start_time == "20230917120000"
        assert programme.stop_time == "20230917130000"
        assert programme.get_default_title() == "Test Programme"
        assert programme.get_default_description() == "Test description"

    @pytest.mark.unit
    def test_programme_xtream_codes_fields(self, test_session):
        """Test Programme model Xtream Codes specific fields."""
        user = create_test_user(test_session)
        server = create_test_server(test_session, owner=user)
        channel = create_test_channel(test_session, user=user, server=server)
        
        programme = create_test_programme(
            test_session,
            channel=channel,
            categories='[{"text": "Movie"}]',
            language='{"text": "en"}',
            length='{"units": "seconds", "value": "7200"}',
            ratings='[{"system": "MPAA", "value": "PG-13"}]'
        )

        categories = programme.get_categories()
        assert categories[0]["text"] == "Movie"
        
        # Length is stored as JSON in the model
        length_data = programme.get_json_field('length')
        assert length_data["value"] == "7200"
        
        # Ratings is stored as JSON array
        ratings_data = programme.get_json_field('ratings')
        assert ratings_data[0]["system"] == "MPAA"
        assert ratings_data[0]["value"] == "PG-13"
