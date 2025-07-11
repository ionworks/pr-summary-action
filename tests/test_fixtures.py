"""Test fixtures for PR summary tests."""

from typing import Dict, Any


class MockGitHubEvents:
    """Mock GitHub event data for testing."""

    @staticmethod
    def get_base_pr_event() -> Dict[str, Any]:
        """Base PR event structure."""
        return {
            "action": "closed",
            "number": 42,
            "pull_request": {
                "id": 123456789,
                "number": 42,
                "state": "closed",
                "locked": False,
                "title": "Test PR",
                "body": "This is a test PR description",
                "created_at": "2023-11-15T10:30:00Z",
                "updated_at": "2023-11-15T11:00:00Z",
                "closed_at": "2023-11-15T11:00:00Z",
                "merged_at": "2023-11-15T11:00:00Z",
                "merged": True,
                "mergeable": True,
                "head": {
                    "sha": "abc123def456",
                    "ref": "feature-branch",
                    "repo": {"name": "test-repo", "full_name": "test-org/test-repo"},
                },
                "base": {
                    "sha": "def456ghi789",
                    "ref": "main",
                    "repo": {"name": "test-repo", "full_name": "test-org/test-repo"},
                },
                "user": {
                    "login": "test-user",
                    "id": 12345,
                    "type": "User",
                    "name": "Test User",
                    "email": "test@example.com",
                },
                "merged_by": {
                    "login": "maintainer",
                    "id": 67890,
                    "type": "User",
                    "name": "Maintainer",
                    "email": "maintainer@example.com",
                },
                "assignees": [],
                "requested_reviewers": [],
                "labels": [],
                "milestone": None,
                "draft": False,
                "html_url": "https://github.com/test-org/test-repo/pull/42",
            },
            "repository": {
                "id": 987654321,
                "name": "test-repo",
                "full_name": "test-org/test-repo",
                "owner": {"login": "test-org", "id": 11111, "type": "Organization"},
            },
            "sender": {"login": "maintainer", "id": 67890, "type": "User"},
        }

    @staticmethod
    def feature_pr_event() -> Dict[str, Any]:
        """Mock GitHub event for a feature PR."""
        event = MockGitHubEvents.get_base_pr_event()
        event["pull_request"].update(
            {
                "title": "Add user authentication with OAuth2",
                "body": "## Summary\nThis PR adds OAuth2 authentication support using Google as the provider.\n\n## Changes\n- Added OAuth2Provider class for handling authentication\n- Implemented login/callback routes\n- Added session management\n- Updated authentication flow\n\n## Testing\n- Added unit tests for OAuth2Provider\n- Tested login flow manually\n- Verified callback handling\n\n## Security Notes\n- Uses HTTPS for all OAuth2 flows\n- Implements CSRF protection with state parameter\n- Session cookies are httpOnly and secure",
                "head": {
                    "sha": "feature123",
                    "ref": "feature/oauth2-auth",
                    "repo": {"name": "test-repo", "full_name": "test-org/test-repo"},
                },
                "labels": [
                    {"name": "feature", "color": "0e8a16"},
                    {"name": "security", "color": "d93f0b"},
                ],
                "user": {
                    "login": "developer1",
                    "id": 12345,
                    "type": "User",
                    "name": "John Developer",
                    "email": "john@example.com",
                },
            }
        )
        return event

    @staticmethod
    def bugfix_pr_event() -> Dict[str, Any]:
        """Mock GitHub event for a bugfix PR."""
        event = MockGitHubEvents.get_base_pr_event()
        event["pull_request"].update(
            {
                "title": "Fix memory leak in session cleanup",
                "body": "## Bug Description\nSession cleanup wasn't properly releasing memory, causing gradual memory leaks.\n\n## Root Cause\nThe cleanup timer wasn't being canceled properly, and callback references weren't being cleared.\n\n## Solution\n- Added proper timer cleanup\n- Implemented callback cleanup in session destruction\n- Added periodic cleanup timer management\n\n## Reproduction\n1. Create multiple sessions\n2. Let them expire\n3. Memory usage increases over time\n\n## Testing\n- Added unit tests for session cleanup\n- Verified memory usage remains stable\n- Tested timer management",
                "head": {
                    "sha": "bugfix456",
                    "ref": "fix/session-memory-leak",
                    "repo": {"name": "test-repo", "full_name": "test-org/test-repo"},
                },
                "labels": [
                    {"name": "bug", "color": "d73a4a"},
                    {"name": "memory", "color": "f9d0c4"},
                ],
                "user": {
                    "login": "developer2",
                    "id": 12346,
                    "type": "User",
                    "name": "Alice Developer",
                    "email": "alice@example.com",
                },
            }
        )
        return event

    @staticmethod
    def docs_pr_event() -> Dict[str, Any]:
        """Mock GitHub event for a documentation PR."""
        event = MockGitHubEvents.get_base_pr_event()
        event["pull_request"].update(
            {
                "title": "Update authentication API documentation",
                "body": "## Documentation Updates\nUpdated the authentication API documentation to reflect the new OAuth2 implementation.\n\n## Changes\n- Added OAuth2 endpoint documentation\n- Updated authentication flow diagrams\n- Added security considerations section\n- Updated error handling documentation\n\n## Review Notes\n- All examples have been tested\n- Links have been verified\n- Screenshots updated",
                "head": {
                    "sha": "docs789",
                    "ref": "docs/update-auth-api",
                    "repo": {"name": "test-repo", "full_name": "test-org/test-repo"},
                },
                "labels": [{"name": "documentation", "color": "0075ca"}],
                "user": {
                    "login": "techwriter1",
                    "id": 12347,
                    "type": "User",
                    "name": "Bob Writer",
                    "email": "bob@example.com",
                },
            }
        )
        return event

    @staticmethod
    def refactor_pr_event() -> Dict[str, Any]:
        """Mock GitHub event for a refactoring PR."""
        event = MockGitHubEvents.get_base_pr_event()
        event["pull_request"].update(
            {
                "title": "Refactor authentication service architecture",
                "body": "## Refactoring Overview\nRefactored the authentication service to use dependency injection and improve testability.\n\n## Changes\n- Introduced IAuthService interface\n- Added dependency injection for user repository and session manager\n- Simplified authentication flow\n- Improved error handling with custom exceptions\n\n## Benefits\n- Better testability with mocked dependencies\n- Cleaner separation of concerns\n- More maintainable code structure\n- Easier to extend with new authentication methods\n\n## Breaking Changes\nNone - all public APIs remain the same.",
                "head": {
                    "sha": "refactor101",
                    "ref": "refactor/auth-service-di",
                    "repo": {"name": "test-repo", "full_name": "test-org/test-repo"},
                },
                "labels": [
                    {"name": "refactor", "color": "fbca04"},
                    {"name": "architecture", "color": "d4c5f9"},
                ],
            }
        )
        return event


class MockPRDiffs:
    """Mock PR diff data for testing."""

    @staticmethod
    def feature_diff() -> str:
        """Mock diff for a feature PR."""
        return (
            "diff --git a/src/auth/oauth.py b/src/auth/oauth.py\n"
            "new file mode 100644\n"
            "index 0000000..123456\n"
            "--- /dev/null\n"
            "+++ b/src/auth/oauth.py\n"
            "@@ -0,0 +1,45 @@\n"
            '+"""OAuth2 authentication implementation."""\n'
            "+\n"
            "+import os\n"
            "+from typing import Optional\n"
            "+from authlib.integrations.flask_client import OAuth\n"
            "+from flask import current_app\n"
            "+\n"
            "+\n"
            "+class OAuth2Provider:\n"
            '+    """OAuth2 authentication provider."""\n'
            "+    \n"
            "+    def __init__(self, app=None):\n"
            "+        self.oauth = OAuth()\n"
            "+        if app:\n"
            "+            self.init_app(app)\n"
            "+    \n"
            "+    def init_app(self, app):\n"
            '+        """Initialize OAuth2 with Flask app."""\n'
            "+        self.oauth.init_app(app)\n"
            "+        \n"
            "+        # Configure Google OAuth2\n"
            "+        self.google = self.oauth.register(\n"
            "+            name='google',\n"
            "+            client_id=os.getenv('GOOGLE_CLIENT_ID'),\n"
            "+            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),\n"
            "+            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',\n"
            "+            client_kwargs={\n"
            "+                'scope': 'openid email profile'\n"
            "+            }\n"
            "+        )\n"
            "+    \n"
            "+    def get_auth_url(self, redirect_uri: str) -> str:\n"
            '+        """Generate authorization URL."""\n'
            "+        return self.google.authorize_redirect(redirect_uri)\n"
            "+    \n"
            "+    def get_user_info(self, token: dict) -> Optional[dict]:\n"
            '+        """Get user information from token."""\n'
            "+        try:\n"
            "+            user_info = self.google.parse_id_token(token)\n"
            "+            return {\n"
            "+                'id': user_info['sub'],\n"
            "+                'email': user_info['email'],\n"
            "+                'name': user_info['name'],\n"
            "+            }\n"
            "+        except Exception:\n"
            "+            return None\n"
            "diff --git a/src/auth/routes.py b/src/auth/routes.py\n"
            "index 789abc..def123 100644\n"
            "--- a/src/auth/routes.py\n"
            "+++ b/src/auth/routes.py\n"
            "@@ -1,5 +1,6 @@\n"
            ' """Authentication routes."""\n'
            " \n"
            "+from flask import Blueprint, session, redirect, url_for, request\n"
            " from .oauth import OAuth2Provider\n"
            " \n"
            " auth_bp = Blueprint('auth', __name__)\n"
            "@@ -10,3 +11,25 @@ oauth_provider = OAuth2Provider()\n"
            " def login():\n"
            '     """Initiate OAuth2 login."""\n'
            "     return oauth_provider.get_auth_url(url_for('auth.callback', _external=True))\n"
            "+\n"
            "+@auth_bp.route('/callback')\n"
            "+def callback():\n"
            '+    """Handle OAuth2 callback."""\n'
            "+    token = oauth_provider.google.authorize_access_token()\n"
            "+    user_info = oauth_provider.get_user_info(token)\n"
            "+    \n"
            "+    if user_info:\n"
            "+        session['user_id'] = user_info['id']\n"
            "+        session['user_email'] = user_info['email']\n"
            "+        session['user_name'] = user_info['name']\n"
            "+        return redirect(url_for('dashboard'))\n"
            "+    \n"
            "+    return redirect(url_for('login', error='auth_failed'))\n"
            "+\n"
            "+@auth_bp.route('/logout')\n"
            "+def logout():\n"
            '+    """Logout user."""\n'
            "+    session.clear()\n"
            "+    return redirect(url_for('home'))\n"
        )

    @staticmethod
    def bugfix_diff() -> str:
        """Mock diff for a bugfix PR."""
        return (
            "diff --git a/src/auth/session.py b/src/auth/session.py\n"
            "index abc123..def456 100644\n"
            "--- a/src/auth/session.py\n"
            "+++ b/src/auth/session.py\n"
            "@@ -15,6 +15,7 @@ class SessionManager:\n"
            "         self.sessions = {}\n"
            "         self.cleanup_interval = 300  # 5 minutes\n"
            "         self.max_age = 3600  # 1 hour\n"
            "+        self._cleanup_timer = None\n"
            "         \n"
            "     def create_session(self, user_id: str) -> str:\n"
            '         """Create a new session."""\n'
            "@@ -35,8 +36,12 @@ class SessionManager:\n"
            "     def cleanup_session(self, session_id: str):\n"
            '         """Clean up a specific session."""\n'
            "         if session_id in self.sessions:\n"
            "-            del self.sessions[session_id]\n"
            "+            session_data = self.sessions.pop(session_id, None)\n"
            "+            if session_data and 'cleanup_callbacks' in session_data:\n"
            "+                for callback in session_data['cleanup_callbacks']:\n"
            "+                    try:\n"
            "+                        callback()\n"
            "+                    except Exception as e:\n"
            '+                        logger.warning(f"Session cleanup callback failed: {e}")\n'
            "             \n"
            "     def cleanup_expired_sessions(self):\n"
            '         """Clean up expired sessions."""\n'
            "@@ -48,6 +53,16 @@ class SessionManager:\n"
            "                 expired_sessions.append(session_id)\n"
            "         \n"
            "         for session_id in expired_sessions:\n"
            "             self.cleanup_session(session_id)\n"
            "+    \n"
            "+    def start_cleanup_timer(self):\n"
            '+        """Start periodic cleanup timer."""\n'
            "+        if self._cleanup_timer:\n"
            "+            self._cleanup_timer.cancel()\n"
            "+        \n"
            "+        self._cleanup_timer = threading.Timer(\n"
            "+            self.cleanup_interval, \n"
            "+            self._periodic_cleanup\n"
            "+        )\n"
            "+        self._cleanup_timer.daemon = True\n"
            "+        self._cleanup_timer.start()\n"
        )

    @staticmethod
    def docs_diff() -> str:
        """Mock diff for a documentation PR."""
        return (
            "diff --git a/docs/api/authentication.md b/docs/api/authentication.md\n"
            "index 111222..333444 100644\n"
            "--- a/docs/api/authentication.md\n"
            "+++ b/docs/api/authentication.md\n"
            "@@ -1,6 +1,8 @@\n"
            " # Authentication API\n"
            " \n"
            "-The Authentication API provides endpoints for user login and logout.\n"
            "+The Authentication API provides endpoints for user authentication using OAuth2.\n"
            "+\n"
            "+## Overview\n"
            " \n"
            " ## Endpoints\n"
            " \n"
            "@@ -15,6 +17,42 @@ POST /auth/login\n"
            " }\n"
            " ```\n"
            " \n"
            "+### OAuth2 Login\n"
            "+\n"
            "+Initiate OAuth2 authentication flow.\n"
            "+\n"
            "+```http\n"
            "+GET /auth/oauth/login\n"
            "+```\n"
            "+\n"
            "+**Response:**\n"
            "+- `302 Redirect` to OAuth2 provider\n"
            "+\n"
            "+### OAuth2 Callback\n"
            "+\n"
            "+Handle OAuth2 callback from provider.\n"
            "+\n"
            "+```http\n"
            "+GET /auth/oauth/callback?code=<authorization_code>&state=<state>\n"
            "+```\n"
            "+\n"
            "+**Parameters:**\n"
            "+- `code` (string): Authorization code from OAuth2 provider\n"
            "+- `state` (string): State parameter for CSRF protection\n"
            "+\n"
            "+**Response:**\n"
            "+- `302 Redirect` to dashboard on success\n"
            "+- `302 Redirect` to login on failure\n"
            "+\n"
            "+## Authentication Flow\n"
            "+\n"
            "+1. User clicks login button\n"
            "+2. Application redirects to `/auth/oauth/login`\n"
            "+3. User is redirected to OAuth2 provider (Google)\n"
            "+4. User authorizes the application\n"
            "+5. OAuth2 provider redirects back to `/auth/oauth/callback`\n"
            "+6. Application validates the authorization code\n"
            "+7. User is logged in and redirected to dashboard\n"
            "+\n"
            " ## Error Handling\n"
            " \n"
            " All authentication endpoints return appropriate HTTP status codes:\n"
            "@@ -22,3 +60,12 @@ All authentication endpoints return appropriate HTTP status codes:\n"
            " - `401 Unauthorized` - Invalid credentials\n"
            " - `403 Forbidden` - Access denied\n"
            " - `500 Internal Server Error` - Server error\n"
            "+\n"
            "+## Security Considerations\n"
            "+\n"
            "+- All OAuth2 flows use HTTPS\n"
            "+- State parameter prevents CSRF attacks\n"
            "+- Session cookies are httpOnly and secure\n"
            "+- Access tokens are not exposed to client-side JavaScript\n"
            "+- Sessions expire after 1 hour of inactivity\n"
            "+- Failed login attempts are rate limited\n"
        )

    @staticmethod
    def refactor_diff() -> str:
        """Mock diff for a refactoring PR."""
        return (
            "diff --git a/src/auth/service.py b/src/auth/service.py\n"
            "index aaa111..bbb222 100644\n"
            "--- a/src/auth/service.py\n"
            "+++ b/src/auth/service.py\n"
            "@@ -1,50 +1,25 @@\n"
            ' """Authentication service."""\n'
            " \n"
            "-import hashlib\n"
            "-import secrets\n"
            "-from typing import Optional, Dict, Any\n"
            "+from typing import Optional\n"
            "+from .interfaces import IAuthService, IUserRepository, ISessionManager\n"
            "+from .exceptions import AuthenticationError, AuthorizationError\n"
            " \n"
            " \n"
            "-class AuthService:\n"
            '-    """Main authentication service."""\n'
            "+class AuthService(IAuthService):\n"
            '+    """OAuth2 authentication service implementation."""\n'
            "     \n"
            "-    def __init__(self):\n"
            "-        self.users = {}\n"
            "-        self.sessions = {}\n"
            "+    def __init__(self, user_repo: IUserRepository, session_manager: ISessionManager):\n"
            "+        self.user_repo = user_repo\n"
            "+        self.session_manager = session_manager\n"
            "     \n"
            "-    def login(self, username: str, password: str) -> Optional[str]:\n"
            '-        """Login user with username and password."""\n'
            "-        if not username or not password:\n"
            "-            return None\n"
            "-        \n"
            "-        user = self.users.get(username)\n"
            "-        if not user:\n"
            "-            return None\n"
            "-        \n"
            "-        # Hash password and compare\n"
            "-        password_hash = hashlib.sha256(password.encode()).hexdigest()\n"
            "-        if user.get('password_hash') != password_hash:\n"
            "-            return None\n"
            "-        \n"
            "-        # Create session\n"
            "-        session_id = secrets.token_hex(32)\n"
            "-        self.sessions[session_id] = {\n"
            "-            'user_id': user['id'],\n"
            "-            'username': username,\n"
            "-            'created_at': datetime.now()\n"
            "-        }\n"
            "-        \n"
            "-        return session_id\n"
            "+    def authenticate_user(self, oauth_token: dict) -> Optional[str]:\n"
            '+        """Authenticate user with OAuth2 token."""\n'
            "+        try:\n"
            "+            user_info = self._extract_user_info(oauth_token)\n"
            "+            user = self.user_repo.find_or_create_user(user_info)\n"
            "+            session_id = self.session_manager.create_session(user.id)\n"
            "+            return session_id\n"
            "+        except Exception as e:\n"
            '+            raise AuthenticationError(f"Authentication failed: {str(e)}")\n'
            "     \n"
            "-    def logout(self, session_id: str) -> bool:\n"
            '-        """Logout user by session ID."""\n'
            "-        if session_id in self.sessions:\n"
            "-            del self.sessions[session_id]\n"
            "-            return True\n"
            "-        return False\n"
            "-    \n"
            "-    def get_user_by_session(self, session_id: str) -> Optional[Dict[str, Any]]:\n"
            '-        """Get user information by session ID."""\n'
            "-        session = self.sessions.get(session_id)\n"
            "-        if not session:\n"
            "-            return None\n"
            "-        \n"
            "-        username = session['username']\n"
            "-        return self.users.get(username)\n"
            "+    def logout_user(self, session_id: str) -> bool:\n"
            '+        """Logout user by session ID."""\n'
            "+        return self.session_manager.cleanup_session(session_id)\n"
        )


class MockOpenAIResponses:
    """Mock OpenAI API responses for testing."""

    @staticmethod
    def feature_summary() -> str:
        """Mock OpenAI response for feature PR."""
        return '{"technical": "Added OAuth2 authentication using Google provider with proper session management and security measures", "marketing": "Enhanced security with modern OAuth2 authentication - users can now log in securely using their Google accounts"}'

    @staticmethod
    def bugfix_summary() -> str:
        """Mock OpenAI response for bugfix PR."""
        return '{"technical": "Fixed memory leak in session cleanup by properly canceling timers and clearing callback references", "marketing": "Improved application performance by fixing a memory leak that could cause the system to slow down over time"}'

    @staticmethod
    def docs_summary() -> str:
        """Mock OpenAI response for documentation PR."""
        return '{"technical": "Updated authentication API documentation to reflect OAuth2 implementation with comprehensive security guidelines", "marketing": "Improved developer experience with updated and comprehensive authentication documentation"}'

    @staticmethod
    def refactor_summary() -> str:
        """Mock OpenAI response for refactoring PR."""
        return '{"technical": "Refactored authentication service to use dependency injection pattern for better testability and maintainability", "marketing": "Enhanced code quality and maintainability through improved architecture - making the system more reliable and easier to extend"}'

    @staticmethod
    def invalid_json_response() -> str:
        """Mock invalid JSON response for error testing."""
        return "This is not valid JSON"

    @staticmethod
    def empty_response() -> str:
        """Mock empty response for error testing."""
        return ""
