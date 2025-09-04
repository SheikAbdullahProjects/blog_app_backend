from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Enum,DateTime
from database import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, index=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    profile_picture_url = Column(String, nullable=True)
    profile_picture_id = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    blogs = relationship("Blog", back_populates="user", cascade="all, delete-orphan")