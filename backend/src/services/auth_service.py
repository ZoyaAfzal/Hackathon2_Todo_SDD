"""Authentication service for user registration and login.

Handles user creation, password hashing, and JWT token generation.
"""

import base64
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional

import jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from src.core.config import settings
from src.models.user import User

# Password hashing context using bcrypt
# bcrypt has a 72-byte password limit - we use pre-hashing to support any password length
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)


def _prehash_password(password: str) -> str:
    """Pre-hash password with SHA256 to handle bcrypt's 72-byte limit.

    bcrypt only uses the first 72 bytes of a password. To support passwords
    of any length securely, we hash the password with SHA256 first, then
    encode it as base64 (resulting in 44 characters, well under 72 bytes).

    Args:
        password: The raw password string

    Returns:
        Base64-encoded SHA256 hash of the password
    """
    # SHA256 hash of the password, encoded as base64
    # This produces a 44-character string (within bcrypt's 72-byte limit)
    password_hash = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(password_hash).decode("ascii")


class AuthService:
    """Service for authentication operations.

    Handles:
    - User registration with password hashing
    - User authentication with password verification
    - JWT token generation
    """

    def __init__(self, session: Session):
        """Initialize auth service with database session.

        Args:
            session: SQLModel database session
        """
        self.session = session

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt with SHA256 pre-hashing.

        Uses SHA256 pre-hashing to handle bcrypt's 72-byte limit while
        maintaining full password entropy for any length password.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        # Pre-hash to handle bcrypt's 72-byte limit
        prehashed = _prehash_password(password)
        return pwd_context.hash(prehashed)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to compare against

        Returns:
            True if password matches, False otherwise
        """
        # Pre-hash to match the format used during hashing
        prehashed = _prehash_password(plain_password)
        return pwd_context.verify(prehashed, hashed_password)

    def create_token(self, user: User) -> str:
        """Create a JWT token for a user.

        Token contains:
        - sub: User ID (subject)
        - email: User's email
        - iat: Issued at timestamp
        - exp: Expiration timestamp (24 hours from now)

        Args:
            user: User entity to create token for

        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "iat": now,
            "exp": now + timedelta(hours=24),
        }
        return jwt.encode(
            payload,
            settings.BETTER_AUTH_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address.

        Args:
            email: Email address to look up

        Returns:
            User if found, None otherwise
        """
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def register(
        self,
        email: str,
        password: str,
        name: Optional[str] = None,
    ) -> tuple[User, str]:
        """Register a new user.

        Creates a new user with hashed password and returns
        the user along with a JWT token.

        Args:
            email: User's email address
            password: Plain text password (will be hashed)
            name: Optional display name

        Returns:
            Tuple of (User, JWT token)

        Raises:
            ValueError: If email is already registered
        """
        # Check if email already exists
        existing_user = self.get_user_by_email(email)
        if existing_user:
            raise ValueError("email_exists")

        # Create new user with hashed password
        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=self.hash_password(password),
            created_at=datetime.utcnow(),
        )

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        # Generate token
        token = self.create_token(user)

        return user, token

    def authenticate(self, email: str, password: str) -> tuple[User, str]:
        """Authenticate a user and return a token.

        Verifies email and password, then generates a new JWT token.

        Args:
            email: User's email address
            password: Plain text password

        Returns:
            Tuple of (User, JWT token)

        Raises:
            ValueError: If credentials are invalid
        """
        # Find user by email
        user = self.get_user_by_email(email)
        if not user:
            raise ValueError("invalid_credentials")

        # Verify password
        if not self.verify_password(password, user.password_hash):
            raise ValueError("invalid_credentials")

        # Generate new token
        token = self.create_token(user)

        return user, token


def get_auth_service(session: Session) -> AuthService:
    """Factory function to create AuthService instance.

    Args:
        session: Database session

    Returns:
        AuthService instance
    """
    return AuthService(session)
