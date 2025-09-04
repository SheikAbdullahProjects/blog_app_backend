from fastapi import HTTPException, Depends, Response, Request
from sqlalchemy.orm import Session
from starlette import status
from typing import Annotated
from .models import User
from .schemas import UserCreate, UserOut
from passlib.context import CryptContext
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from database import get_db

load_dotenv()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db_dependency = Annotated[Session, Depends(get_db)]

EXPIRES_AT = os.getenv("ACCESS_TOKEN_EXPIRE_TIME")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def check_user_for_signup(db : Session, email):
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User already exists")

def check_user_exists(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def check_password(user, password):
    if not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
def hash_password(password):
    return bcrypt_context.hash(password)

def create_access_token(response : Response,email : str, id : int):
    encode = {
        "sub" : email,
        "id" : id
    }
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=int(EXPIRES_AT))
    encode.update({"exp" : expires_at})
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    response.set_cookie(
        key="access_token",
        value=token,
        secure=True,
        httponly=True,
        samesite="none",
        max_age= 60*60*24
    )
    
    

def create_user_srv(db : Session,response : Response, user_model : UserCreate):
    if user_model.password != user_model.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    hashed_password = hash_password(user_model.password)
    user = User(hashed_password=hashed_password,**user_model.model_dump(exclude={"password", "confirm_password"}))
    db.add(user)
    db.commit()
    db.refresh(user)
    create_access_token(response, user.email, user.id)
    return user

def authenticate_user(db: Session, response : Response, email: str, password: str):
    user = check_user_exists(db, email)
    check_password(user, password)
    create_access_token(response, user.email, user.id)
    return user

def get_current_user(request : Request, db : db_dependency) -> UserOut:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email : str = payload.get("sub")
        id : int = payload.get("id")
        if not email or not id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = check_user_exists(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return UserOut.model_validate(user, from_attributes=True)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
def check_user_admin(user):
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only have access")