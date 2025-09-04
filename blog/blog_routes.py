from fastapi import APIRouter, HTTPException, Depends, Path, UploadFile, File, Form
from starlette import status
from typing import Annotated, List, Optional
from sqlalchemy.orm import Session
from database import get_db
from .schemas import BlogOut
from auth.schemas import UserOut
from auth.service import get_current_user, check_user_admin
from clodinary_srv import upload_img, delete_img
from .service import check_fields, create_blog_srv, all_blogs, single_blog, check_blog_owner, update_blog_srv, all_blogs_by_owners, single_blog_for_publish, all_blogs_for_publish
from auth.service import check_user_exists

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[UserOut, Depends(get_current_user)]


router = APIRouter(
    prefix="/blog",
    tags=["Blog"]
)

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[BlogOut])
async def get_all_blogs(db : db_dependency, current_user : user_dependency):
    try:
        blogs = all_blogs(db)
        return blogs
    except Exception as exp:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exp))
@router.get("/all-blogs", status_code=status.HTTP_200_OK, response_model=List[BlogOut])
async def get_all_blogs_for_publish(db : db_dependency, current_user : user_dependency):
    try:
        blogs = all_blogs_for_publish(db)
        return blogs
    except Exception as exp:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exp))
@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=BlogOut)
async def get_single_blog(db : db_dependency, current_user : user_dependency, id : int = Path(ge=1)):
    try:
        blog = single_blog(db, id)
        return blog
    except Exception as exp:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exp))
        
@router.get("/unpublished/{id}", status_code=status.HTTP_200_OK, response_model=BlogOut)
async def get_single_blog_unpublished(db : db_dependency, current_user : user_dependency, id : int = Path(ge=1)):
    try:
        blog = single_blog_for_publish(db, id)
        return blog
    except Exception as exp:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exp))
        

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=BlogOut)
async def create_blog(db : db_dependency, current_user : user_dependency, title : str = Form (...), description : str = Form (...), file : UploadFile = File(...)):
    try:
        print(title, description, file)
        check_fields(title, description, file.file)
        result = upload_img(file.file, folder_name="blogs")
        image_url = result["secure_url"]
        image_id = result["public_id"]
        blog = create_blog_srv(db, title, description, image_url, image_id, current_user.id)
        return blog
        
    except Exception as exp:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exp))
    
@router.put("/update/{id}", status_code=status.HTTP_200_OK, response_model=BlogOut)
async def update_blog(db : db_dependency, current_user : user_dependency, id : int = Path(ge=1), title : Optional[str] = Form (None), description : Optional[str] = Form (None), file : Optional[UploadFile] = File(None)):
    try:
        blog = single_blog(db, id)
        image_url = None
        image_id = None
        check_blog_owner(owner_id=blog.owner_id, user_id=current_user.id)
        print(title, description, file)
        if file:
            if blog.image_id:
                delete_img(blog.image_id)
                print("Deleted old image from cloudinary")
            result = upload_img(file.file, folder_name="blogs")
            image_url = result["secure_url"]
            image_id = result["public_id"]
            
        updated_blog = update_blog_srv(db, blog, title, description, image_url, image_id)
        return updated_blog
        
    except Exception as exp:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exp))
    
@router.get("/blogs-owners/", status_code=status.HTTP_200_OK, response_model=List[BlogOut])
async def get_blogs_with_owners(db : db_dependency, current_user : user_dependency):
    try:
        blogs = all_blogs_by_owners(db, current_user.id)
        return blogs
    except Exception as exp:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exp))
    
@router.put("/admin/publish/{id}", status_code=status.HTTP_200_OK, response_model=BlogOut)
async def publish_blog(db : db_dependency, current_user : user_dependency, id : int = Path(ge=1)):
    try:
        user = check_user_exists(db, current_user.email)
        check_user_admin(user)
        blog = single_blog_for_publish(db, id)
        blog.is_published = True
        db.commit()
        db.refresh(blog)
        return blog
    except Exception as exp:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exp))


