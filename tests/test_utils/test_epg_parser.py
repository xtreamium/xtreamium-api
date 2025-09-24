import pytest
from unittest.mock import patch, MagicMock, mock_open, AsyncMock
import os
import tempfile
from app.utils.epg_parser import EPGParser


class TestEPGParser:
    """Test cases for EPG parser class."""

    @pytest.mark.unit
    def test_epg_parser_initialization(self):
        """Test EPG parser initialization."""
        parser = EPGParser(
            url="http://example.com/epg.xml",
            server_id=123,
            user_id="test-user-456"
        )
        
        assert parser._epg_url == "http://example.com/epg.xml"
        assert parser._server_id == 123
        assert parser._user_id == "test-user-456"
        assert parser._programs == {}
        
        # Check cache file path is created
        assert "test-user-456" in parser._cache_file
        assert "123" in parser._cache_file
        assert parser._cache_file.endswith("epg.xml")

    @pytest.mark.unit
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_cache_directory_creation(self, mock_makedirs, mock_exists):
        """Test cache directory is created if it doesn't exist."""
        mock_exists.return_value = False
        
        parser = EPGParser(
            url="http://example.com/epg.xml",
            server_id=123,
            user_id="test-user-456"
        )
        
        # makedirs should be called to create the cache directory
        mock_makedirs.assert_called_once()

    @pytest.mark.unit
    @patch('os.path.exists')
    def test_cache_directory_not_created_if_exists(self, mock_exists):
        """Test cache directory is not created if it already exists."""
        mock_exists.return_value = True
        
        with patch('os.makedirs') as mock_makedirs:
            parser = EPGParser(
                url="http://example.com/epg.xml",
                server_id=123,
                user_id="test-user-456"
            )
            
            # makedirs should not be called if directory exists
            mock_makedirs.assert_not_called()

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('app.utils.epg_parser.requests.get')
    @patch('app.utils.epg_parser.parse_xmltv_file')
    @patch('app.utils.epg_parser.store_epg_channels')
    @patch('app.utils.epg_parser.is_file_older_cache_time')
    @patch('os.path.isfile')
    async def test_cache_epg_downloads_when_cache_old(self, mock_isfile, mock_is_old, 
                                                     mock_store_channels, mock_parse_file, 
                                                     mock_requests_get, test_session):
        """Test EPG caching downloads when cache is old or doesn't exist."""
        # Setup mocks
        mock_isfile.return_value = True
        mock_is_old.return_value = True  # Cache is old
        mock_requests_get.return_value.content = b"<tv></tv>"
        mock_parse_file.return_value = []
        mock_store_channels.return_value = {'channels': 0, 'programmes': 0}
        
        parser = EPGParser(
            url="http://example.com/epg.xml",
            server_id=123,
            user_id="test-user-456"
        )
        
        with patch('builtins.open', mock_open()) as mock_file:
            await parser.cache_epg(test_session)
            
            # Should download EPG
            mock_requests_get.assert_called_once_with("http://example.com/epg.xml", timeout=30)
            # Should write to cache file
            mock_file.assert_called_once()
            # Should parse the file
            mock_parse_file.assert_called_once()
            # Should store in database
            mock_store_channels.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('app.utils.epg_parser.is_file_older_cache_time')
    @patch('os.path.isfile')
    async def test_cache_epg_skips_download_when_cache_fresh(self, mock_isfile, mock_is_old, test_session):
        """Test EPG caching skips download when cache is fresh."""
        # Setup mocks
        mock_isfile.return_value = True
        mock_is_old.return_value = False  # Cache is fresh
        
        parser = EPGParser(
            url="http://example.com/epg.xml",
            server_id=123,
            user_id="test-user-456"
        )
        
        with patch('app.utils.epg_parser.requests.get') as mock_requests_get:
            await parser.cache_epg(test_session)
            
            # Should not download EPG
            mock_requests_get.assert_not_called()

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('app.utils.epg_parser.requests.get')
    async def test_cache_epg_handles_download_error(self, mock_requests_get, test_session):
        """Test EPG caching handles download errors gracefully."""
        # Setup mock to raise exception
        mock_requests_get.side_effect = Exception("Network error")
        
        parser = EPGParser(
            url="http://example.com/epg.xml",
            server_id=123,
            user_id="test-user-456"
        )
        
        with patch('os.path.isfile', return_value=False):
            # Should not raise exception
            await parser.cache_epg(test_session)
            
            # Verify download was attempted
            mock_requests_get.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('app.services.data.epg_data_services.get_channel_by_xmltv_id')
    @patch('app.services.data.epg_data_services.get_programmes_for_channel')
    async def test_get_listings_returns_programmes_for_channel(self, mock_get_programmes, 
                                                              mock_get_channel, test_session):
        """Test get_listings returns programmes for a specific channel."""
        # Create mock channel object
        mock_channel = MagicMock()
        mock_channel.id = "channel-123"
        
        mock_get_channel.return_value = mock_channel
        mock_get_programmes.return_value = ["programme1", "programme2"]
        
        parser = EPGParser(
            url="http://example.com/epg.xml",
            server_id=123,
            user_id="test-user-456"
        )
        
        result = await parser.get_listings("test.channel", test_session)
        
        assert result == ["programme1", "programme2"]
        mock_get_channel.assert_called_once_with("test-user-456", 123, "test.channel", test_session)
        mock_get_programmes.assert_called_once_with("channel-123", test_session)

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('app.services.data.epg_data_services.get_channel_by_xmltv_id')
    async def test_get_listings_returns_empty_for_unknown_channel(self, mock_get_channel, test_session):
        """Test get_listings returns empty list for unknown channel."""
        mock_get_channel.return_value = None
        
        parser = EPGParser(
            url="http://example.com/epg.xml",
            server_id=123,
            user_id="test-user-456"
        )
        
        result = await parser.get_listings("unknown.channel", test_session)
        
        assert result == []
        mock_get_channel.assert_called_once_with("test-user-456", 123, "unknown.channel", test_session)