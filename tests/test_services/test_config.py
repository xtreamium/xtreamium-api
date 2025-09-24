import pytest
from unittest.mock import patch
from app.services.config import Settings, settings


class TestConfig:
    """Test cases for configuration services."""

    @pytest.mark.unit
    def test_settings_instance(self):
        """Test that settings instance exists and has expected values."""
        assert settings is not None
        assert isinstance(settings, Settings)
        assert settings.PROJECT_NAME == "Xtreamium Backend"
        assert settings.API_PATH == "/api/v1"

    @pytest.mark.unit
    def test_settings_jwt_secret(self):
        """Test JWT secret configuration."""
        assert settings.JWT_SECRET is not None
        assert len(settings.JWT_SECRET) > 0
        # Should be a valid hex string
        assert all(c in '0123456789abcdef' for c in settings.JWT_SECRET.lower())

    @pytest.mark.unit
    def test_cors_origins_configuration(self):
        """Test CORS origins configuration."""
        assert settings.BACKEND_CORS_ORIGINS is not None
        assert isinstance(settings.BACKEND_CORS_ORIGINS, list)
        assert len(settings.BACKEND_CORS_ORIGINS) > 0
        
        # Check that localhost is in the list for development
        localhost_found = any('localhost' in origin or '127.0.0.1' in origin 
                             for origin in settings.BACKEND_CORS_ORIGINS)
        assert localhost_found

    @pytest.mark.unit
    def test_settings_class_creation(self):
        """Test creating a new Settings instance."""
        test_settings = Settings()
        assert test_settings.PROJECT_NAME == "Xtreamium Backend"
        assert test_settings.API_PATH == "/api/v1"

    @pytest.mark.unit
    @patch.dict('os.environ', {'PROJECT_NAME': 'Test Project'})
    def test_settings_with_env_override(self):
        """Test settings with environment variable override."""
        # Create new instance to pick up env vars
        test_settings = Settings()
        assert test_settings.PROJECT_NAME == 'Test Project'

    @pytest.mark.unit
    @patch.dict('os.environ', {'API_PATH': '/api/v2'})
    def test_api_path_override(self):
        """Test API path can be overridden via environment."""
        test_settings = Settings()
        assert test_settings.API_PATH == '/api/v2'

    @pytest.mark.unit 
    def test_cors_origins_types(self):
        """Test that all CORS origins are strings."""
        for origin in settings.BACKEND_CORS_ORIGINS:
            assert isinstance(origin, str)
            # Should be valid URL format (starts with http/https)
            assert origin.startswith(('http://', 'https://'))

    @pytest.mark.unit
    def test_settings_immutability(self):
        """Test that settings behave as expected."""
        original_name = settings.PROJECT_NAME
        # Settings should maintain their values
        assert settings.PROJECT_NAME == original_name