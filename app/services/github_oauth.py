"""GitHub OAuth service for authentication."""
import httpx

from app.services.config import settings
from app.services.logger import get_logger

logger = get_logger(__name__)


class GitHubOAuthService:
    """Service for handling GitHub OAuth authentication."""

    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GITHUB_USER_URL = "https://api.github.com/user"
    GITHUB_USER_EMAILS_URL = "https://api.github.com/user/emails"

    @staticmethod
    async def exchange_code_for_token(code: str) -> dict:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from GitHub OAuth

        Returns:
            dict: Token response including access_token

        Raises:
            httpx.HTTPError: If token exchange fails
        """
        logger.debug("Exchanging GitHub authorization code for access token")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                GitHubOAuthService.GITHUB_TOKEN_URL,
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                },
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            token_data = response.json()

            if "error" in token_data:
                logger.error(f"GitHub token exchange error: {token_data.get('error_description')}")
                raise ValueError(f"GitHub OAuth error: {token_data.get('error_description')}")

            logger.info("Successfully exchanged code for access token")
            return token_data

    @staticmethod
    async def get_user_info(access_token: str) -> dict:
        """
        Get user information from GitHub using access token.

        Args:
            access_token: GitHub access token

        Returns:
            dict: User information including id, login, name, email, etc.

        Raises:
            httpx.HTTPError: If request fails
        """
        logger.debug("Fetching user info from GitHub")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient() as client:
            # Get user profile
            response = await client.get(
                GitHubOAuthService.GITHUB_USER_URL,
                headers=headers,
            )
            response.raise_for_status()
            user_info = response.json()

            # If email is not public, fetch from emails endpoint
            if not user_info.get("email"):
                logger.debug("Email not public, fetching from emails endpoint")
                emails_response = await client.get(
                    GitHubOAuthService.GITHUB_USER_EMAILS_URL,
                    headers=headers,
                )
                emails_response.raise_for_status()
                emails = emails_response.json()

                # Find primary verified email
                primary_email = next(
                    (e["email"] for e in emails if e.get("primary") and e.get("verified")),
                    None
                )
                if primary_email:
                    user_info["email"] = primary_email
                elif emails:
                    # Fallback to first verified email
                    verified_email = next(
                        (e["email"] for e in emails if e.get("verified")),
                        None
                    )
                    if verified_email:
                        user_info["email"] = verified_email

            logger.info(f"Successfully fetched user info for: {user_info.get('login')}")
            return user_info


github_oauth_service = GitHubOAuthService()
