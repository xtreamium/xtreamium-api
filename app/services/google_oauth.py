"""Google OAuth service for authentication."""
import httpx
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.services.config import settings
from app.services.logger import get_logger

logger = get_logger(__name__)


class GoogleOAuthService:
    """Service for handling Google OAuth authentication."""

    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    @staticmethod
    async def verify_id_token(token: str) -> dict:
        """
        Verify Google ID token and return user info.

        Args:
            token: The Google ID token to verify

        Returns:
            dict: User information from the token

        Raises:
            ValueError: If token verification fails
        """
        try:
            idinfo = id_token.verify_oauth2_token(
                token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
            )

            if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
                raise ValueError("Wrong issuer.")

            logger.info(f"Successfully verified Google token for user: {idinfo.get('email')}")
            return idinfo

        except ValueError as e:
            logger.error(f"Token verification failed: {e}")
            raise

    @staticmethod
    async def exchange_code_for_token(code: str) -> dict:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from Google OAuth

        Returns:
            dict: Token response including access_token and id_token

        Raises:
            httpx.HTTPError: If token exchange fails
        """
        logger.debug("Exchanging authorization code for access token")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                GoogleOAuthService.GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            response.raise_for_status()
            token_data = response.json()

            logger.info("Successfully exchanged code for access token")
            return token_data

    @staticmethod
    async def get_user_info(access_token: str) -> dict:
        """
        Get user information from Google using access token.

        Args:
            access_token: Google access token

        Returns:
            dict: User information including email, name, picture, etc.

        Raises:
            httpx.HTTPError: If request fails
        """
        logger.debug("Fetching user info from Google")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                GoogleOAuthService.GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            user_info = response.json()

            logger.info(f"Successfully fetched user info for: {user_info.get('email')}")
            return user_info


google_oauth_service = GoogleOAuthService()
