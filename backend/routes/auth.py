
from datetime import timedelta

from auth.dependencies import get_current_user
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends

from auth.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from database.connection import db
from models.user import UserRegister, UserLogin, UserResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])

users_collection = db["users"]


@router.post("/register", response_model=UserResponse,
             status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister):
    username = user.username.strip().lower()
    email = str(user.email).strip().lower()

    # Prevent duplicate usernames and email addresses
    existing_user = users_collection.find_one({
        "$or": [
            {"username": username},
            {"email": email},
        ]
    })

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        )

    # Public registration always creates a worker.
    # Admin accounts must be created through a trusted process.
    new_user = {
        "name": user.name.strip(),
        "username": username,
        "email": email,
        "password_hash": hash_password(user.password),
        "role": "worker",
        "worker_type": user.worker_type,
    }

    result = users_collection.insert_one(new_user)

    return UserResponse(
        id=str(result.inserted_id),
        name=new_user["name"],
        username=new_user["username"],
        email=new_user["email"],
        role=new_user["role"],
        worker_type=new_user["worker_type"],
    )


@router.post("/login")
def login_user(credentials: UserLogin):
    username = credentials.username.strip().lower()

    user = users_collection.find_one({
        "username": username
    })

    if not user or not verify_password(
        credentials.password,
        user["password_hash"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={
            "sub": str(user["_id"]),
            "role": user["role"],
        },
        expires_delta=timedelta(minutes=60),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "username": user["username"],
            "role": user["role"],
            "worker_type": user.get("worker_type"),
        },
    }
    

@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: dict = Depends(get_current_user),
):
    return UserResponse(
        id=str(current_user["_id"]),
        name=current_user["name"],
        username=current_user["username"],
        email=current_user["email"],
        role=current_user["role"],
        worker_type=current_user.get("worker_type"),
    )