from pydantic import BaseModel
from datetime import datetime
from auth.schemas import UserOut


class BlogBase(BaseModel):
    title : str
    description : str
    
class BlogOut(BlogBase):
    id : int
    image_url : str
    image_id : str
    avg_rating : float
    is_published : bool
    user : UserOut
    created_at : datetime
    updated_at : datetime
    
    class Config:
        from_attributes = True