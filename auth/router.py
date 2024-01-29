from datetime import timedelta
from typing import Annotated

from fastapi import HTTPException

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session


from auth.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from auth.crud import create_user
from auth.schemas import UserCreate, User, Token
from database import get_db
from auth.utils import authenticate, create_access_token, validate_access_token

user_router = APIRouter(responses={404: {'description': 'Not found'}})


@user_router.post('/', status_code=status.HTTP_201_CREATED, response_model=Token)
def create_users(user: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Username already exists",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


@user_router.post("/login")
async def login_for_access_token(user: UserCreate, db: Session = Depends(get_db)) -> Token:
    user = authenticate(db, user.email, user.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


@user_router.get("/me", response_model=User)
def read_users_me(current_user: Annotated[User, Depends(validate_access_token)]):
    return current_user
