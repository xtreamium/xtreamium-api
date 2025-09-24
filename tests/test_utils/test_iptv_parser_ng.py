import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from app.utils.iptv_parser_ng import Channel, Programme, XMLTVParser


class TestXMLTVParser:
    """Test cases for XMLTV parser functionality."""

    @pytest.mark.unit
    def test_channel_creation(self):
        """Test creating a channel object."""
        channel = Channel(
            id="test.channel",
            display_names=[{"lang": "en", "text": "Test Channel"}],
            icons=[{"src": "http://example.com/icon.png"}],
            urls=[{"value": "http://example.com/stream"}]
        )
        
        assert channel.id == "test.channel"
        assert len(channel.display_names) == 1
        assert channel.display_names[0]["text"] == "Test Channel"
        assert len(channel.icons) == 1
        assert len(channel.programmes) == 0

    @pytest.mark.unit
    def test_programme_creation(self):
        """Test creating a programme object."""
        programme = Programme(
            start="20231001120000 +0000",
            stop="20231001130000 +0000",
            channel="test.channel",
            titles=[{"lang": "en", "text": "Test Programme"}],
            descriptions=[{"lang": "en", "text": "A test programme"}],
            categories=[{"lang": "en", "text": "Entertainment"}]
        )
        
        assert programme.start == "20231001120000 +0000"
        assert programme.stop == "20231001130000 +0000"
        assert programme.channel == "test.channel"
        assert programme.titles[0]["text"] == "Test Programme"
        assert programme.categories[0]["text"] == "Entertainment"

    @pytest.mark.unit
    def test_programme_defaults(self):
        """Test programme object with default values."""
        programme = Programme(
            start="20231001120000 +0000",
            channel="test.channel"
        )
        
        assert programme.stop is None
        assert programme.clumpidx == "0/1"
        assert programme.new is False
        assert len(programme.titles) == 0
        assert len(programme.descriptions) == 0

    @pytest.mark.unit
    def test_programme_with_video_audio_info(self):
        """Test programme with video and audio information."""
        programme = Programme(
            start="20231001120000 +0000",
            channel="test.channel",
            video={"aspect": "16:9", "quality": "HDTV"},
            audio={"stereo": "stereo"}
        )
        
        assert programme.video is not None
        assert programme.video["aspect"] == "16:9"
        assert programme.video["quality"] == "HDTV"
        assert programme.audio is not None
        assert programme.audio["stereo"] == "stereo"

    @pytest.mark.unit 
    def test_programme_with_ratings(self):
        """Test programme with rating information."""
        programme = Programme(
            start="20231001120000 +0000",
            channel="test.channel",
            ratings=[{"system": "MPAA", "value": "PG-13"}]
        )
        
        assert len(programme.ratings) == 1
        assert programme.ratings[0]["system"] == "MPAA"
        assert programme.ratings[0]["value"] == "PG-13"

    @pytest.mark.unit
    def test_xmltv_parser_initialization(self):
        """Test XMLTVParser initialization."""
        parser = XMLTVParser()
        assert parser is not None
        # Add more specific tests once we see the parser implementation

    @pytest.mark.unit
    def test_channel_with_multiple_display_names(self):
        """Test channel with multiple display names in different languages."""
        channel = Channel(
            id="multi.channel",
            display_names=[
                {"lang": "en", "text": "Test Channel"},
                {"lang": "es", "text": "Canal de Prueba"},
                {"lang": "fr", "text": "Chaîne de Test"}
            ]
        )
        
        assert len(channel.display_names) == 3
        en_name = next(name for name in channel.display_names if name["lang"] == "en")
        assert en_name["text"] == "Test Channel"
        
        es_name = next(name for name in channel.display_names if name["lang"] == "es")
        assert es_name["text"] == "Canal de Prueba"

    @pytest.mark.unit
    def test_programme_with_episode_info(self):
        """Test programme with episode numbering information."""
        programme = Programme(
            start="20231001120000 +0000",
            channel="test.channel",
            titles=[{"lang": "en", "text": "TV Series"}],
            episode_nums=[
                {"system": "xmltv_ns", "text": "1.5.0/1"},
                {"system": "onscreen", "text": "S02E06"}
            ]
        )
        
        assert len(programme.episode_nums) == 2
        xmltv_ep = next(ep for ep in programme.episode_nums if ep["system"] == "xmltv_ns")
        assert xmltv_ep["text"] == "1.5.0/1"
        
        onscreen_ep = next(ep for ep in programme.episode_nums if ep["system"] == "onscreen")
        assert onscreen_ep["text"] == "S02E06"

    @pytest.mark.unit
    def test_programme_with_credits(self):
        """Test programme with cast and crew information."""
        programme = Programme(
            start="20231001120000 +0000",
            channel="test.channel",
            credits={
                "director": [{"text": "John Director"}],
                "actor": [
                    {"text": "Jane Actor", "role": "Main Character"},
                    {"text": "Bob Actor", "role": "Supporting"}
                ],
                "writer": [{"text": "Script Writer"}]
            }
        )
        
        assert "director" in programme.credits
        assert "actor" in programme.credits
        assert "writer" in programme.credits
        assert len(programme.credits["actor"]) == 2
        assert programme.credits["actor"][0]["role"] == "Main Character"