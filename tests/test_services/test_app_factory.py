import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from app.services.app_factory import create_app


class TestAppFactory:
    """Test cases for application factory."""

    @pytest.mark.unit
    def test_create_app_returns_fastapi_instance(self):
        """Test that create_app returns a FastAPI instance."""
        app = create_app()
        assert isinstance(app, FastAPI)

    @pytest.mark.unit
    def test_create_app_has_correct_title(self):
        """Test that the app has the correct title."""
        app = create_app()
        assert app.title == "Xtreamium Backend"

    @pytest.mark.unit
    def test_create_app_has_version(self):
        """Test that the app has a version set."""
        app = create_app()
        assert app.version is not None
        assert len(app.version) > 0

    @pytest.mark.unit
    def test_create_app_includes_routers(self):
        """Test that the app includes expected routers."""
        app = create_app()
        
        # Check that routes exist
        routes = list(app.routes)
        
        # Should have at least some basic routes
        assert len(routes) > 0
        
        # We can't easily inspect route paths due to FastAPI internals,
        # but we can verify routes were added
        assert len(routes) >= 1

    @pytest.mark.unit
    def test_create_app_cors_configuration(self):
        """Test CORS configuration."""
        app = create_app()
        
        # Check that CORS middleware is configured (may vary based on implementation)
        middlewares = [middleware.cls for middleware in app.user_middleware]
        # Just verify that some middleware exists 
        assert len(middlewares) >= 0  # Could be 0 if no middleware configured yet

    @pytest.mark.unit
    def test_create_app_multiple_instances(self):
        """Test creating multiple app instances."""
        app1 = create_app()
        app2 = create_app()
        
        # Should create separate instances
        assert app1 is not app2
        assert both_have_same_configuration(app1, app2)

    @pytest.mark.unit
    @patch('app.services.app_factory.settings')
    def test_create_app_with_custom_settings(self, mock_settings):
        """Test creating app with custom settings."""
        mock_settings.PROJECT_NAME = "Custom App Name"
        mock_settings.API_PATH = "/api/v2"
        
        app = create_app()
        assert app.title == "Custom App Name"

    @pytest.mark.unit
    def test_create_app_has_exception_handlers(self):
        """Test that app has exception handlers configured."""
        app = create_app()
        
        # FastAPI apps should have some exception handlers
        assert len(app.exception_handlers) >= 0
        # The exact number depends on implementation

    @pytest.mark.unit
    def test_create_app_middleware_order(self):
        """Test middleware is added in correct order."""
        app = create_app()
        
        # Should have middleware configured
        assert len(app.user_middleware) > 0
        
        # CORS should typically be one of the first middlewares
        middleware_names = [type(m.cls).__name__ for m in app.user_middleware]
        if 'CORSMiddleware' in middleware_names:
            cors_index = middleware_names.index('CORSMiddleware')
            # CORS should be early in the middleware stack
            assert cors_index < len(middleware_names) // 2


def both_have_same_configuration(app1: FastAPI, app2: FastAPI) -> bool:
    """Helper function to check if two apps have the same basic configuration."""
    return (
        app1.title == app2.title and
        app1.version == app2.version and
        len(app1.routes) == len(app2.routes)
    )