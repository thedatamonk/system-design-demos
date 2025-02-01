from sqlalchemy import Integer, Column, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from blog_db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=128), unique=True, index=True)
    email = Column(String(length=128), unique=True, index=True)
    total_published_blogs = Column(Integer, default=0)
    blogs = relationship("Blog", back_populates="owner")

class Blog(Base):
    __tablename__ = "blogs"
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(length=256), index=True)
    content = Column(Text)
    published_at = Column(DateTime, nullable=True)
    owner = relationship("User", back_populates="blogs")


