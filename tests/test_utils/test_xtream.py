import pytest
from unittest.mock import Mock, patch, AsyncMock
import json

from app.utils.XTream import XTream


class TestXtreamCodes:
    """Test cases for Xtream Codes integration."""

    @pytest.mark.xtream
    def test_xtream_initialization(self):
        """Test Xtream API client initialization."""
        client = XTream(
            server="http://example.com:8080",
            username="testuser",
            password="testpass"
        )

        assert client._server == "http://example.com:8080"
        assert client._username == "testuser"
        assert client._password == "testpass"

    @pytest.mark.xtream
    def test_xtream_initialization_validation(self):
        """Test Xtream initialization validates required parameters."""
        # Test missing server
        with pytest.raises(ValueError):
            XTream(server="", username="testuser", password="testpass")

        # Test missing username
        with pytest.raises(ValueError):
            XTream(server="http://example.com", username="", password="testpass")

        # Test missing password
        with pytest.raises(ValueError):
            XTream(server="http://example.com", username="testuser", password="")

    @pytest.mark.xtream
    @patch('requests.get')
    def test_authentication_url_generation(self, mock_get):
        """Test authentication URL generation."""
        mock_response = Mock()
        mock_response.json.return_value = {"user_info": {"username": "testuser"}}
        mock_get.return_value = mock_response

        client = XTream("http://example.com:8080", "testuser", "testpass")
        response = client._authenticate()

        # Verify the correct URL was called
        expected_url = "http://example.com:8080/player_api.php?username=testuser&password=testpass"
        mock_get.assert_called_with(expected_url)

    @pytest.mark.xtream
    def test_live_categories_url_generation(self):
        """Test live categories URL generation."""
        client = XTream("http://example.com:8080", "testuser", "testpass")

        # Use the private method to test URL generation
        url = client._XTream__get_live_categories_url()
        expected = "http://example.com:8080/player_api.php?username=testuser&password=testpass&action=get_live_categories"
        assert url == expected

    @pytest.mark.xtream
    def test_live_streams_by_category_url(self):
        """Test live streams by category URL generation."""
        client = XTream("http://example.com:8080", "testuser", "testpass")

        url = client._XTream__get_live_streams_by_category_url("123")
        expected = "http://example.com:8080/player_api.php?username=testuser&password=testpass&action=get_live_streams&category_id=123"
        assert url == expected

    @pytest.mark.xtream
    @patch('requests.get')
    def test_cache_usage(self, mock_get):
        """Test that authentication data is cached."""
        mock_response = Mock()
        test_auth_data = {"user_info": {"username": "testuser", "status": "Active"}}
        mock_response.json.return_value = test_auth_data
        mock_get.return_value = mock_response

        client = XTream("http://example.com:8080", "testuser", "testpass")
        client._authenticate()

        # Verify auth data is stored in cache
        assert client._cache.auth_data == test_auth_data
