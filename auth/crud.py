import sqlalchemy.exc
from sqlalchemy.orm import Session

from auth.models import User
from auth.schemas import UserCreate
from auth.utils import encrypt_password


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate):
    try:
        user = User(email=user.email, hashed_password=encrypt_password(user.password))
        db.add(user)
        db.commit()
        db.refresh(user)
    except sqlalchemy.exc.IntegrityError:
        return None
    return user
