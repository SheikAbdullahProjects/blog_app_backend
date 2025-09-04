from fastapi import HTTPException
from starlette import status
from sqlalchemy.orm import Session
from .models import Blog
from typing import Optional

def check_fields(title, description, file):
    if len(title) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title must have minimum length of 5")
    if len(description) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title must have minimum length of 5")
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide image")
    
def create_blog_srv(db : Session, title : str, description : str, image_url : str, image_id : str, user_id : int):
    blog = Blog(title=title, description=description, image_url=image_url, image_id=image_id, owner_id=user_id)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog

def all_blogs(db : Session):
    blogs = db.query(Blog).filter(Blog.is_published).all()
    return blogs
def all_blogs_for_publish(db : Session):
    blogs = db.query(Blog).filter(Blog.is_published == False).all()
    return blogs
def all_blogs_by_owners(db : Session, id : int):
    blogs = db.query(Blog).filter(Blog.owner_id == id).all()
    return blogs


def single_blog_for_publish(db : Session, id : int):
    print(id)
    blog = db.query(Blog).filter(Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    return blog


def single_blog(db : Session, id : int):
    blog = db.query(Blog).filter(Blog.is_published, Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    return blog

def check_blog_owner(owner_id, user_id):
    if owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have access to update a blog")

def update_blog_srv(
    db: Session,
    blog,
    title: Optional[str] = None,
    description: Optional[str] = None,
    image_url: Optional[str] = None,
    image_id: Optional[str] = None
):
    if title:
        blog.title = title
    if description:
        blog.description = description
    if image_url and image_id:
        blog.image_url = image_url
        blog.image_id = image_id

    db.commit()
    db.refresh(blog)
    return blog