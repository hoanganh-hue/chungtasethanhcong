"""
Authentication System for OpenManus-Youtu Integrated Framework
JWT-based authentication and session management
"""

import jwt
import hashlib
import secrets
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    DEVELOPER = "developer"


@dataclass
class User:
    """User data class."""
    id: str
    username: str
    email: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = None
    last_login: datetime = None


@dataclass
class AuthToken:
    """Authentication token data class."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600


class JWTManager:
    """JWT token management."""
    
    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = algorithm
        self.access_token_expiry = 3600  # 1 hour
        self.refresh_token_expiry = 86400 * 7  # 7 days
    
    def generate_access_token(self, user: User) -> str:
        """Generate access token."""
        payload = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "exp": datetime.utcnow() + timedelta(seconds=self.access_token_expiry),
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def generate_refresh_token(self, user: User) -> str:
        """Generate refresh token."""
        payload = {
            "user_id": user.id,
            "exp": datetime.utcnow() + timedelta(seconds=self.refresh_token_expiry),
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token."""
        payload = self.verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            return None
        
        # Create new access token
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        # In a real implementation, you would fetch user from database
        user = User(
            id=user_id,
            username="user",  # Fetch from database
            email="user@example.com",  # Fetch from database
            role=UserRole.USER
        )
        
        return self.generate_access_token(user)


class PasswordManager:
    """Password management utilities."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using PBKDF2."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        return f"{salt}:{password_hash.hex()}"
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        try:
            salt, stored_hash = hashed_password.split(':')
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return password_hash.hex() == stored_hash
        except ValueError:
            return False


class AuthenticationManager:
    """Main authentication manager."""
    
    def __init__(self):
        self.jwt_manager = JWTManager()
        self.password_manager = PasswordManager()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.max_failed_attempts = 5
        self.lockout_duration = 300  # 5 minutes
    
    async def authenticate_user(self, username: str, password: str) -> Optional[AuthToken]:
        """Authenticate user with username and password."""
        # Check for account lockout
        if self._is_account_locked(username):
            logger.warning(f"Account locked for user: {username}")
            return None
        
        # In a real implementation, you would fetch user from database
        user = await self._get_user_by_username(username)
        if not user:
            self._record_failed_attempt(username)
            return None
        
        # Verify password
        if not self._verify_user_password(user, password):
            self._record_failed_attempt(username)
            return None
        
        # Clear failed attempts on successful login
        if username in self.failed_attempts:
            del self.failed_attempts[username]
        
        # Generate tokens
        access_token = self.jwt_manager.generate_access_token(user)
        refresh_token = self.jwt_manager.generate_refresh_token(user)
        
        # Store session
        session_id = secrets.token_urlsafe(32)
        self.active_sessions[session_id] = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        
        # Update last login
        user.last_login = datetime.utcnow()
        
        logger.info(f"User authenticated successfully: {username}")
        
        return AuthToken(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    async def verify_token(self, token: str) -> Optional[User]:
        """Verify token and return user."""
        payload = self.jwt_manager.verify_token(token)
        
        if not payload or payload.get("type") != "access":
            return None
        
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        # In a real implementation, you would fetch user from database
        user = await self._get_user_by_id(user_id)
        if not user or not user.is_active:
            return None
        
        return user
    
    async def refresh_token(self, refresh_token: str) -> Optional[AuthToken]:
        """Refresh access token."""
        new_access_token = self.jwt_manager.refresh_access_token(refresh_token)
        
        if not new_access_token:
            return None
        
        # Generate new refresh token
        payload = self.jwt_manager.verify_token(refresh_token)
        if not payload:
            return None
        
        user = await self._get_user_by_id(payload.get("user_id"))
        if not user:
            return None
        
        new_refresh_token = self.jwt_manager.generate_refresh_token(user)
        
        return AuthToken(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
    
    async def logout(self, token: str) -> bool:
        """Logout user and invalidate token."""
        payload = self.jwt_manager.verify_token(token)
        
        if not payload:
            return False
        
        # In a real implementation, you would add token to blacklist
        logger.info(f"User logged out: {payload.get('username')}")
        return True
    
    def _is_account_locked(self, username: str) -> bool:
        """Check if account is locked due to failed attempts."""
        if username not in self.failed_attempts:
            return False
        
        failed_attempts = self.failed_attempts[username]
        recent_attempts = [
            attempt for attempt in failed_attempts
            if datetime.utcnow() - attempt < timedelta(seconds=self.lockout_duration)
        ]
        
        if len(recent_attempts) >= self.max_failed_attempts:
            return True
        
        # Clean old attempts
        self.failed_attempts[username] = recent_attempts
        return False
    
    def _record_failed_attempt(self, username: str):
        """Record failed login attempt."""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = []
        
        self.failed_attempts[username].append(datetime.utcnow())
        
        # Clean old attempts
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.lockout_duration)
        self.failed_attempts[username] = [
            attempt for attempt in self.failed_attempts[username]
            if attempt > cutoff_time
        ]
    
    async def _get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username (mock implementation)."""
        # In a real implementation, this would query the database
        if username == "admin":
            return User(
                id="1",
                username="admin",
                email="admin@example.com",
                role=UserRole.ADMIN,
                created_at=datetime.utcnow()
            )
        elif username == "user":
            return User(
                id="2",
                username="user",
                email="user@example.com",
                role=UserRole.USER,
                created_at=datetime.utcnow()
            )
        return None
    
    async def _get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID (mock implementation)."""
        # In a real implementation, this would query the database
        if user_id == "1":
            return User(
                id="1",
                username="admin",
                email="admin@example.com",
                role=UserRole.ADMIN,
                created_at=datetime.utcnow()
            )
        elif user_id == "2":
            return User(
                id="2",
                username="user",
                email="user@example.com",
                role=UserRole.USER,
                created_at=datetime.utcnow()
            )
        return None
    
    def _verify_user_password(self, user: User, password: str) -> bool:
        """Verify user password (mock implementation)."""
        # In a real implementation, this would verify against stored hash
        if user.username == "admin" and password == "admin123":
            return True
        elif user.username == "user" and password == "user123":
            return True
        return False
    
    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get active sessions."""
        return self.active_sessions.copy()
    
    def cleanup_expired_sessions(self):
        """Cleanup expired sessions."""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            if current_time - session_data["last_activity"] > timedelta(hours=24):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")


# Global authentication manager
auth_manager = AuthenticationManager()