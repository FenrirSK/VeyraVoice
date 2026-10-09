
from pydantic import BaseModel, Field, EmailStr
from typing import Literal, Optional


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    role: Literal["admin", "worker"] = "worker"

    worker_type: Optional[
        Literal[
            "carpenter",
            "electrician",
            "plumber",
            "painter",
            "other"
        ]
    ] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    username: str
    email: EmailStr
    role: str
    worker_type: Optional[str] = None