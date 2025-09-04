from fastapi import APIRouter, HTTPException, Depends, Request, Response, UploadFile, File
from starlette import status
from typing import Annotated, Optional
from .schemas import UserCreate, UserOut, UserLogin
from sqlalchemy.orm import Session
from database import get_db
from .service import check_user_for_signup, create_user_srv, authenticate_user, get_current_user, check_user_exists
from clodinary_srv import upload_img, delete_img


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[UserOut, Depends(get_current_user)]


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def create_user(db : db_dependency, response : Response, user_model : UserCreate):
    try:
        check_user_for_signup(db, user_model.email)
        user = create_user_srv(db, response, user_model)
        return user
    except Exception as exp:
        print(str(exp))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exp))
    
@router.post("/signin", status_code=status.HTTP_200_OK, response_model=UserOut)
async def verify_user(db : db_dependency, response : Response, user_model : UserLogin):
    try:
        user = authenticate_user(db, response, user_model.email, user_model.password)
        return user
    except Exception as exp:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exp))
    
@router.post("/signout", status_code=status.HTTP_200_OK)
async def logout_user(response : Response):
    try:
        response.delete_cookie(key="access_token")
        return {"detail": "Successfully logged out"}
    except Exception as exp:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exp))
    
@router.get("/current-user", status_code=status.HTTP_200_OK, response_model=UserOut)
async def current_user(user: user_dependency):
    try:
        return user
    except Exception as exp:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exp))
    
@router.put("/update-user", status_code=status.HTTP_200_OK, response_model=UserOut)
async def update_user(db : db_dependency, current_user : user_dependency, file : UploadFile = File(...)):
    try:
        user = check_user_exists(db, current_user.email)
        if user.profile_picture_id:
            delete_img(user.profile_picture_id)
        result = upload_img(file.file, folder_name="profiles")
        user.profile_picture_url = result.get("secure_url")
        user.profile_picture_id = result.get("public_id")
        db.commit()
        db.refresh(user)
        return user
    except Exception as exp:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exp))
    