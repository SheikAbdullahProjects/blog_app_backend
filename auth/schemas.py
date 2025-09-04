from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username : str
    email : EmailStr
    
class UserCreate(UserBase):
    password : str
    confirm_password : str
    
class UserLogin(BaseModel):
    email : EmailStr
    password : str
    
    
class UserUpdate(BaseModel):
    username : Optional[str] = None
    email : Optional[EmailStr] = None
    
class UserOut(UserBase):
    id : int
    is_admin : bool
    profile_picture_url: Optional[str] = None
    profile_picture_id: Optional[str] = None
    created_at : datetime
    updated_at : datetime
    
    class Config:
        from_attributes = True