"""
Test fixtures for PR Summary Action tests.
Contains realistic mock data for various PR scenarios.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any


class MockGitHubEvents:
    """Mock GitHub event payloads for different PR scenarios."""
    
    @staticmethod
    def get_base_pr_event() -> Dict[str, Any]:
        """Base PR event structure."""
        return {
            "action": "closed",
            "number": 42,
            "repository": {
                "id": 123456789,
                "name": "test-repo",
                "full_name": "testorg/test-repo",
                "private": False,
                "default_branch": "main",
                "html_url": "https://github.com/testorg/test-repo",
            },
            "sender": {
                "login": "testuser",
                "id": 12345,
                "type": "User",
                "html_url": "https://github.com/testuser",
            },
        }

    @staticmethod
    def feature_pr_event() -> Dict[str, Any]:
        """Mock event for a feature PR."""
        base = MockGitHubEvents.get_base_pr_event()
        base["pull_request"] = {
            "id": 987654321,
            "number": 42,
            "title": "Add user authentication with OAuth2",
            "body": """## Description
This PR adds OAuth2 authentication support to the application.

## Changes
- Added OAuth2 provider configuration
- Implemented login/logout flow
- Added user session management
- Updated middleware for authentication checks

## Testing
- [ ] Unit tests for auth service
- [ ] Integration tests for login flow
- [ ] Manual testing with Google OAuth

## Security
- Secrets are stored in environment variables
- Session cookies are httpOnly and secure
- CSRF protection implemented

Fixes #123""",
            "state": "closed",
            "merged": True,
            "merged_at": "2024-01-15T10:30:00Z",
            "created_at": "2024-01-14T09:00:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "html_url": "https://github.com/testorg/test-repo/pull/42",
            "user": {
                "login": "developer1",
                "id": 11111,
                "name": "John Developer",
                "type": "User",
                "html_url": "https://github.com/developer1",
            },
            "merged_by": {
                "login": "maintainer1",
                "id": 22222,
                "name": "Jane Maintainer",
                "type": "User",
                "html_url": "https://github.com/maintainer1",
            },
            "base": {
                "ref": "main",
                "sha": "abc123",
                "repo": {
                    "name": "test-repo",
                    "full_name": "testorg/test-repo",
                },
            },
            "head": {
                "ref": "feature/oauth2-auth",
                "sha": "def456",
                "repo": {
                    "name": "test-repo",
                    "full_name": "testorg/test-repo",
                },
            },
            "labels": [
                {"name": "feature", "color": "0e8a16"},
                {"name": "security", "color": "ee0701"},
            ],
            "milestone": {
                "title": "v2.0.0",
                "number": 1,
            },
            "assignees": [
                {
                    "login": "developer1",
                    "id": 11111,
                    "html_url": "https://github.com/developer1",
                }
            ],
            "requested_reviewers": [
                {
                    "login": "reviewer1",
                    "id": 33333,
                    "html_url": "https://github.com/reviewer1",
                }
            ],
        }
        return base

    @staticmethod
    def bugfix_pr_event() -> Dict[str, Any]:
        """Mock event for a bugfix PR."""
        base = MockGitHubEvents.get_base_pr_event()
        base["pull_request"] = {
            "id": 987654322,
            "number": 43,
            "title": "Fix memory leak in user session handling",
            "body": """## Bug Description
Users were experiencing memory leaks during long sessions due to improper cleanup of session data.

## Root Cause
Session objects were not being properly garbage collected when users logged out.

## Fix
- Added proper cleanup in logout handler
- Implemented session timeout mechanism
- Fixed event listeners that were not being removed

## Testing
- [x] Reproduced the memory leak
- [x] Verified fix resolves the issue
- [x] Added regression tests

Fixes #456""",
            "state": "closed",
            "merged": True,
            "merged_at": "2024-01-15T11:00:00Z",
            "created_at": "2024-01-15T08:00:00Z",
            "updated_at": "2024-01-15T11:00:00Z",
            "html_url": "https://github.com/testorg/test-repo/pull/43",
            "user": {
                "login": "developer2",
                "id": 44444,
                "name": "Alice Developer",
                "type": "User",
                "html_url": "https://github.com/developer2",
            },
            "merged_by": {
                "login": "maintainer1",
                "id": 22222,
                "name": "Jane Maintainer",
                "type": "User",
                "html_url": "https://github.com/maintainer1",
            },
            "base": {"ref": "main", "sha": "abc124"},
            "head": {"ref": "bugfix/session-memory-leak", "sha": "def457"},
            "labels": [
                {"name": "bug", "color": "d73a4a"},
                {"name": "critical", "color": "b60205"},
            ],
            "milestone": None,
            "assignees": [],
            "requested_reviewers": [],
        }
        return base

    @staticmethod
    def docs_pr_event() -> Dict[str, Any]:
        """Mock event for a documentation PR."""
        base = MockGitHubEvents.get_base_pr_event()
        base["pull_request"] = {
            "id": 987654323,
            "number": 44,
            "title": "Update API documentation with new endpoints",
            "body": """## Documentation Updates
Updated API documentation to include new authentication endpoints.

## Changes
- Added OAuth2 endpoint documentation
- Updated examples with new authentication flow
- Fixed typos in existing documentation
- Added troubleshooting section

## Review Notes
- All examples have been tested
- Screenshots updated with new UI""",
            "state": "closed",
            "merged": True,
            "merged_at": "2024-01-15T12:00:00Z",
            "created_at": "2024-01-15T09:30:00Z",
            "updated_at": "2024-01-15T12:00:00Z",
            "html_url": "https://github.com/testorg/test-repo/pull/44",
            "user": {
                "login": "techwriter1",
                "id": 55555,
                "name": "Bob Writer",
                "type": "User",
                "html_url": "https://github.com/techwriter1",
            },
            "merged_by": {
                "login": "techwriter1",
                "id": 55555,
                "name": "Bob Writer",
                "type": "User",
                "html_url": "https://github.com/techwriter1",
            },
            "base": {"ref": "main", "sha": "abc125"},
            "head": {"ref": "docs/api-updates", "sha": "def458"},
            "labels": [
                {"name": "documentation", "color": "0075ca"},
            ],
            "milestone": None,
            "assignees": [],
            "requested_reviewers": [],
        }
        return base

    @staticmethod
    def refactor_pr_event() -> Dict[str, Any]:
        """Mock event for a refactoring PR."""
        base = MockGitHubEvents.get_base_pr_event()
        base["pull_request"] = {
            "id": 987654324,
            "number": 45,
            "title": "Refactor authentication service for better maintainability",
            "body": """## Refactoring Goals
Improve code maintainability and testability of the authentication service.

## Changes
- Split large AuthService class into smaller, focused classes
- Extracted interface for better dependency injection
- Added comprehensive unit tests
- Improved error handling with custom exceptions
- Updated documentation

## Performance Impact
- No performance regression expected
- Slight improvement in memory usage due to better object lifecycle management

## Migration Notes
- All public APIs remain unchanged
- Internal implementation details have changed
- Updated all internal references""",
            "state": "closed",
            "merged": True,
            "merged_at": "2024-01-15T14:00:00Z",
            "created_at": "2024-01-14T16:00:00Z",
            "updated_at": "2024-01-15T14:00:00Z",
            "html_url": "https://github.com/testorg/test-repo/pull/45",
            "user": {
                "login": "developer3",
                "id": 66666,
                "name": "Charlie Developer",
                "type": "User",
                "html_url": "https://github.com/developer3",
            },
            "merged_by": {
                "login": "maintainer2",
                "id": 77777,
                "name": "David Maintainer",
                "type": "User",
                "html_url": "https://github.com/maintainer2",
            },
            "base": {"ref": "main", "sha": "abc126"},
            "head": {"ref": "refactor/auth-service", "sha": "def459"},
            "labels": [
                {"name": "refactoring", "color": "e4e669"},
                {"name": "improvement", "color": "a2eeef"},
            ],
            "milestone": {
                "title": "Tech Debt Sprint",
                "number": 2,
            },
            "assignees": [
                {
                    "login": "developer3",
                    "id": 66666,
                    "html_url": "https://github.com/developer3",
                }
            ],
            "requested_reviewers": [
                {
                    "login": "architect1",
                    "id": 88888,
                    "html_url": "https://github.com/architect1",
                }
            ],
        }
        return base


class MockPRDiffs:
    """Mock PR diffs for different scenarios."""
    
    @staticmethod
    def feature_diff() -> str:
        """Mock diff for a feature PR."""
        return """diff --git a/src/auth/oauth.py b/src/auth/oauth.py
new file mode 100644
index 0000000..123456
--- /dev/null
+++ b/src/auth/oauth.py
@@ -0,0 +1,45 @@
+"""OAuth2 authentication implementation."""
+
+import os
+from typing import Optional
+from authlib.integrations.flask_client import OAuth
+from flask import current_app
+
+
+class OAuth2Provider:
+    """OAuth2 authentication provider."""
+    
+    def __init__(self, app=None):
+        self.oauth = OAuth()
+        if app:
+            self.init_app(app)
+    
+    def init_app(self, app):
+        """Initialize OAuth2 with Flask app."""
+        self.oauth.init_app(app)
+        
+        # Configure Google OAuth2
+        self.google = self.oauth.register(
+            name='google',
+            client_id=os.getenv('GOOGLE_CLIENT_ID'),
+            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
+            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
+            client_kwargs={
+                'scope': 'openid email profile'
+            }
+        )
+    
+    def get_auth_url(self, redirect_uri: str) -> str:
+        """Generate authorization URL."""
+        return self.google.authorize_redirect(redirect_uri)
+    
+    def get_user_info(self, token: dict) -> Optional[dict]:
+        """Get user information from token."""
+        try:
+            user_info = self.google.parse_id_token(token)
+            return {
+                'id': user_info['sub'],
+                'email': user_info['email'],
+                'name': user_info['name'],
+            }
+        except Exception:
+            return None
diff --git a/src/auth/routes.py b/src/auth/routes.py
index 789abc..def123 100644
--- a/src/auth/routes.py
+++ b/src/auth/routes.py
@@ -1,5 +1,6 @@
 """Authentication routes."""
 
+from flask import Blueprint, session, redirect, url_for, request
 from .oauth import OAuth2Provider
 
 auth_bp = Blueprint('auth', __name__)
@@ -10,3 +11,25 @@ oauth_provider = OAuth2Provider()
 def login():
     """Initiate OAuth2 login."""
     return oauth_provider.get_auth_url(url_for('auth.callback', _external=True))
+
+@auth_bp.route('/callback')
+def callback():
+    """Handle OAuth2 callback."""
+    token = oauth_provider.google.authorize_access_token()
+    user_info = oauth_provider.get_user_info(token)
+    
+    if user_info:
+        session['user_id'] = user_info['id']
+        session['user_email'] = user_info['email']
+        session['user_name'] = user_info['name']
+        return redirect(url_for('dashboard'))
+    
+    return redirect(url_for('login', error='auth_failed'))
+
+@auth_bp.route('/logout')
+def logout():
+    """Logout user."""
+    session.clear()
+    return redirect(url_for('home'))
"""

    @staticmethod
    def bugfix_diff() -> str:
        """Mock diff for a bugfix PR."""
        return """diff --git a/src/auth/session.py b/src/auth/session.py
index abc123..def456 100644
--- a/src/auth/session.py
+++ b/src/auth/session.py
@@ -15,6 +15,7 @@ class SessionManager:
         self.sessions = {}
         self.cleanup_interval = 300  # 5 minutes
         self.max_age = 3600  # 1 hour
+        self._cleanup_timer = None
         
     def create_session(self, user_id: str) -> str:
         """Create a new session."""
@@ -35,8 +36,12 @@ class SessionManager:
     def cleanup_session(self, session_id: str):
         """Clean up a specific session."""
         if session_id in self.sessions:
-            del self.sessions[session_id]
+            session_data = self.sessions.pop(session_id, None)
+            if session_data and 'cleanup_callbacks' in session_data:
+                for callback in session_data['cleanup_callbacks']:
+                    try:
+                        callback()
+                    except Exception as e:
+                        logger.warning(f"Session cleanup callback failed: {e}")
             
     def cleanup_expired_sessions(self):
         """Clean up expired sessions."""
@@ -48,6 +53,16 @@ class SessionManager:
                 expired_sessions.append(session_id)
         
         for session_id in expired_sessions:
             self.cleanup_session(session_id)
+    
+    def start_cleanup_timer(self):
+        """Start periodic cleanup timer."""
+        if self._cleanup_timer:
+            self._cleanup_timer.cancel()
+        
+        self._cleanup_timer = threading.Timer(
+            self.cleanup_interval, 
+            self._periodic_cleanup
+        )
+        self._cleanup_timer.daemon = True
+        self._cleanup_timer.start()
"""

    @staticmethod
    def docs_diff() -> str:
        """Mock diff for a documentation PR."""
        return """diff --git a/docs/api/authentication.md b/docs/api/authentication.md
index 111222..333444 100644
--- a/docs/api/authentication.md
+++ b/docs/api/authentication.md
@@ -1,6 +1,8 @@
 # Authentication API
 
-The Authentication API provides endpoints for user login and logout.
+The Authentication API provides endpoints for user authentication using OAuth2.
+
+## Overview
 
 ## Endpoints
 
@@ -15,6 +17,42 @@ POST /auth/login
 }
 ```
 
+### OAuth2 Login
+
+Initiate OAuth2 authentication flow.
+
+```http
+GET /auth/oauth/login
+```
+
+**Response:**
+- `302 Redirect` to OAuth2 provider
+
+### OAuth2 Callback
+
+Handle OAuth2 callback from provider.
+
+```http
+GET /auth/oauth/callback?code=<authorization_code>&state=<state>
+```
+
+**Parameters:**
+- `code` (string): Authorization code from OAuth2 provider
+- `state` (string): State parameter for CSRF protection
+
+**Response:**
+- `302 Redirect` to dashboard on success
+- `302 Redirect` to login on failure
+
+## Authentication Flow
+
+1. User clicks login button
+2. Application redirects to `/auth/oauth/login`
+3. User is redirected to OAuth2 provider (Google)
+4. User authorizes the application
+5. OAuth2 provider redirects back to `/auth/oauth/callback`
+6. Application validates the authorization code
+7. User is logged in and redirected to dashboard
+
 ## Error Handling
 
 All authentication endpoints return appropriate HTTP status codes:
@@ -22,3 +60,12 @@ All authentication endpoints return appropriate HTTP status codes:
 - `401 Unauthorized` - Invalid credentials
 - `403 Forbidden` - Access denied
 - `500 Internal Server Error` - Server error
+
+## Security Considerations
+
+- All OAuth2 flows use HTTPS
+- State parameter prevents CSRF attacks
+- Session cookies are httpOnly and secure
+- Access tokens are not exposed to client-side JavaScript
+- Sessions expire after 1 hour of inactivity
+- Failed login attempts are rate limited
"""

    @staticmethod
    def refactor_diff() -> str:
        """Mock diff for a refactoring PR."""
        return """diff --git a/src/auth/service.py b/src/auth/service.py
index aaa111..bbb222 100644
--- a/src/auth/service.py
+++ b/src/auth/service.py
@@ -1,50 +1,25 @@
 """Authentication service."""
 
-import hashlib
-import secrets
-from typing import Optional, Dict, Any
+from typing import Optional
+from .interfaces import IAuthService, IUserRepository, ISessionManager
+from .exceptions import AuthenticationError, AuthorizationError
 
 
-class AuthService:
-    """Main authentication service."""
+class AuthService(IAuthService):
+    """OAuth2 authentication service implementation."""
     
-    def __init__(self):
-        self.users = {}
-        self.sessions = {}
+    def __init__(self, user_repo: IUserRepository, session_manager: ISessionManager):
+        self.user_repo = user_repo
+        self.session_manager = session_manager
     
-    def login(self, username: str, password: str) -> Optional[str]:
-        """Login user with username and password."""
-        if not username or not password:
-            return None
-        
-        user = self.users.get(username)
-        if not user:
-            return None
-        
-        # Hash password and compare
-        password_hash = hashlib.sha256(password.encode()).hexdigest()
-        if user.get('password_hash') != password_hash:
-            return None
-        
-        # Create session
-        session_id = secrets.token_hex(32)
-        self.sessions[session_id] = {
-            'user_id': user['id'],
-            'username': username,
-            'created_at': datetime.now()
-        }
-        
-        return session_id
+    def authenticate_user(self, oauth_token: dict) -> Optional[str]:
+        """Authenticate user with OAuth2 token."""
+        try:
+            user_info = self._extract_user_info(oauth_token)
+            user = self.user_repo.find_or_create_user(user_info)
+            session_id = self.session_manager.create_session(user.id)
+            return session_id
+        except Exception as e:
+            raise AuthenticationError(f"Authentication failed: {str(e)}")
     
-    def logout(self, session_id: str) -> bool:
-        """Logout user by session ID."""
-        if session_id in self.sessions:
-            del self.sessions[session_id]
-            return True
-        return False
-    
-    def get_user_by_session(self, session_id: str) -> Optional[Dict[str, Any]]:
-        """Get user information by session ID."""
-        session = self.sessions.get(session_id)
-        if not session:
-            return None
-        
-        username = session['username']
-        return self.users.get(username)
+    def logout_user(self, session_id: str) -> bool:
+        """Logout user by session ID."""
+        return self.session_manager.cleanup_session(session_id)
"""


class MockOpenAIResponses:
    """Mock OpenAI API responses for testing."""
    
    @staticmethod
    def feature_summary() -> str:
        """Mock OpenAI response for feature PR."""
        return '{"technical": "Added OAuth2 authentication support with Google provider integration, including secure session management and proper cleanup mechanisms for user login/logout flows.", "marketing": "Users can now securely log in using their Google accounts with a streamlined authentication experience."}'
    
    @staticmethod
    def bugfix_summary() -> str:
        """Mock OpenAI response for bugfix PR."""
        return '{"technical": "Fixed critical memory leak in session handling by implementing proper cleanup callbacks and periodic garbage collection of expired sessions.", "marketing": "Improved application stability and performance during extended user sessions."}'
    
    @staticmethod
    def docs_summary() -> str:
        """Mock OpenAI response for documentation PR."""
        return '{"technical": "Updated API documentation to include OAuth2 endpoints, security considerations, and complete authentication flow examples with proper error handling.", "marketing": "Developers now have comprehensive documentation for implementing secure authentication in their applications."}'
    
    @staticmethod
    def refactor_summary() -> str:
        """Mock OpenAI response for refactoring PR."""
        return '{"technical": "Refactored authentication service into smaller, focused classes with dependency injection and improved error handling using custom exceptions.", "marketing": "Enhanced code maintainability and testing capabilities for more reliable authentication features."}'
    
    @staticmethod
    def invalid_json_response() -> str:
        """Mock invalid JSON response for error testing."""
        return "Here's a summary of the changes: The PR adds new authentication features..."
    
    @staticmethod
    def empty_response() -> str:
        """Mock empty response for error testing."""
        return "" 