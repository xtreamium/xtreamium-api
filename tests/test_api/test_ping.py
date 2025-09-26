import pytest
from fastapi import status


class TestPingEndpoint:
    """Test cases for the ping endpoint."""

    @pytest.mark.integration
    def test_ping_endpoint(self, client):
        """Test that the ping endpoint returns successful response."""
        response = client.get("/api/v1/ping")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "ping" in data
        assert data["ping"] == "pong"
        assert data["status"] == "ok"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_ping_endpoint_async(self, async_client):
        """Test ping endpoint with async client."""
        response = await async_client.get("/api/v1/ping", follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "ping" in data
        assert data["ping"] == "pong"
