from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from typing import Annotated
from sqlalchemy.orm import Session
from database import get_db


db_dependency = Annotated[Session, Depends(get_db)]


router = APIRouter(
    prefix="/review",
    tags=["Review"]
)
