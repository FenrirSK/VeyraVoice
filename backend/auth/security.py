import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import  jwt
from passlib.context import CryptContext


# Secret key used to sign JWT tokens


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

# Algorithm used for JWT
ALGORITHM = "HS256"

# Token expiration time
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# Password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """Hash a user's password."""
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """Check whether a password matches its hash."""
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token."""

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt