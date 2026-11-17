import json
import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import UserCreate, UserRead
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class FirebaseSessionRequest(BaseModel):
    id_token: str = Field(min_length=1)
    name: str | None = Field(default=None, max_length=100)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Annotated[Session, Depends(get_db)]) -> User:
    email = str(payload.email).lower()
    existing_user = db.scalar(select(User).where(User.email == email))
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

    user = User(
        name=payload.name,
        email=email,
        password_hash=hash_password(payload.password),
        role="citizen",
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    email = str(payload.email).lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or user.password_hash is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(user.id, user.role), role=user.role)


def _firebase_auth_client():
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    if not project_id:
        raise HTTPException(status_code=503, detail="Google and phone sign-in are not configured")

    try:
        import firebase_admin
        from firebase_admin import auth as firebase_auth
        from firebase_admin import credentials

        try:
            firebase_app = firebase_admin.get_app()
        except ValueError:
            service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
            if service_account:
                credential = credentials.Certificate(json.loads(service_account))
                firebase_app = firebase_admin.initialize_app(
                    credential, {"projectId": project_id}
                )
            else:
                firebase_app = firebase_admin.initialize_app(options={"projectId": project_id})
        return firebase_auth, firebase_app
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Firebase authentication is unavailable") from exc


@router.post("/firebase", response_model=TokenResponse)
def firebase_session(
    payload: FirebaseSessionRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    firebase_auth, firebase_app = _firebase_auth_client()
    try:
        identity = firebase_auth.verify_id_token(payload.id_token, app=firebase_app)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Firebase sign-in could not be verified") from exc

    provider = identity.get("firebase", {}).get("sign_in_provider")
    if provider not in {"google.com", "phone"}:
        raise HTTPException(status_code=403, detail="Use Google or phone verification to sign in")

    firebase_uid = identity["uid"]
    raw_email = identity.get("email")
    verified_email = raw_email.strip().lower() if raw_email and identity.get("email_verified") else None
    phone_number = identity.get("phone_number")
    if provider == "google.com" and not verified_email:
        raise HTTPException(status_code=401, detail="A verified Google email is required")
    if provider == "phone" and not phone_number:
        raise HTTPException(status_code=401, detail="Verified phone number is missing")

    matches = []
    by_uid = db.scalar(select(User).where(User.firebase_uid == firebase_uid))
    if by_uid is not None:
        matches.append(by_uid)
    if verified_email:
        by_email = db.scalar(select(User).where(User.email == verified_email))
        if by_email is not None:
            matches.append(by_email)
    if phone_number:
        by_phone = db.scalar(select(User).where(User.phone_number == phone_number))
        if by_phone is not None:
            matches.append(by_phone)

    matched_users = {user.id: user for user in matches}
    if len(matched_users) > 1:
        raise HTTPException(status_code=409, detail="This Google account and phone number belong to different users")
    user = next(iter(matched_users.values()), None)
    if user is not None and user.firebase_uid not in (None, firebase_uid):
        raise HTTPException(status_code=409, detail="This account is linked to another Firebase identity")

    display_name = (identity.get("name") or payload.name or "").strip()
    if user is None:
        user = User(
            name=display_name or verified_email or phone_number or "CivicConnect user",
            email=verified_email,
            password_hash=None,
            firebase_uid=firebase_uid,
            phone_number=phone_number,
            role="citizen",
        )
        db.add(user)
    else:
        user.firebase_uid = firebase_uid
        if user.email is None and verified_email:
            user.email = verified_email
        if user.phone_number is None and phone_number:
            user.phone_number = phone_number
        if not user.name and display_name:
            user.name = display_name

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="This Google account or phone number is already linked") from exc
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id, user.role), role=user.role)


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user
