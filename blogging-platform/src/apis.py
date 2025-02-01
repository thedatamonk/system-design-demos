from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse


from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from blog_db import SessionLocal, engine, Base
import models
from datetime import datetime, timezone
import httpx

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
template = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    async with httpx.AsyncClient() as client:
        body_params = {
            "sort_by": "published_at",
            "limit": 5
        }

        response = await client.get("http://localhost:8000/blogs", params=body_params)
        blogs = response.json()

    return template.TemplateResponse("index.html", context={"request": request, "blogs": blogs})

@app.get("/contact", response_class=HTMLResponse)
async def homepage(request: Request):
    # currently we are just returning a static template on the home page
    return template.TemplateResponse("contact.html", context={"request": request})

@app.get("/blog", response_class=HTMLResponse)
async def homepage(request: Request):
    # currently we are just returning a static template on the home page
    return template.TemplateResponse("blogpost.html", context={"request": request})

@app.get("/search", response_class=HTMLResponse)
async def homepage(request: Request):
    # currently we are just returning a static template on the home page
    return template.TemplateResponse("search.html", context={"request": request})

# create the database tables
Base.metadata.create_all(bind=engine)

# Dependency to get the DB session
# Every API that needs to interact with the DB will use this dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# define the pydantic models
# these will be used in the APIs to define the request and response bodies
class UserCreate(BaseModel):
    name: str
    email: str

# Note blog creation is different from blog publishing
class BlogCreate(BaseModel):
    title: str
    content: str


# What this means is that while editing a blog the title can't be left blank
# While the content can be left blank
class BlogEdit(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


# User APIs
# /users/new - create new user
@app.post("/users/new")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# /users/{user_id} - get user with user_id. this will particularly be invoked to get user details when displaying the same on the profile page
@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Blog APIS
# /{user_id}/blogs/new - create new blog for user with user_id
@app.post("/{user_id}/blog/publish")
def create_blog(user_id: int, blog: BlogCreate, db: Session = Depends(get_db)):
    db_blog = models.Blog(title=blog.title, content=blog.content, author_id=user_id, published_at=datetime.now(timezone.utc))
    user = db.query(models.User).filter(models.User.id == user_id).first()
    user.total_published_blogs += 1  # update the total number of blogs published by the user
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    db.refresh(user)

    # Redirect the user to the home page after publishing the blog
    return RedirectResponse(url="/", status_code=303)

# /{user_id}/blogs/{blog_id}/edit - edit blog with blog_id for user with user_id
@app.put("/{user_id}/blogs/{blog_id}/edit")
def edit_blog(user_id: int, blog_id: int, blog: BlogEdit, db: Session = Depends(get_db)):
    db_blog = db.query(models.Blog).filter(models.Blog.id == blog_id, models.Blog.author_id == user_id).first()
    if db_blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    if blog.title:
        db_blog.title = blog.title
    if blog.content:
        db_blog.content = blog.content
    db.commit()
    db.refresh(db_blog)
    return db_blog

# /{user_id}/blogs/{blog_id}/delete - delete blog with blog_id for user with user_id
@app.delete("/{user_id}/blogs/{blog_id}/delete")
def delete_blog(user_id: int, blog_id: int, db: Session = Depends(get_db)):
    db_blog = db.query(models.Blog).filter(models.Blog.id == blog_id, models.Blog.author_id == user_id).first()
    if db_blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    db.delete(db_blog)
    db.commit()
    return {"detail": "Blog deleted"}

# /{user_id}/blogs/search?keyword={keyword}
@app.get("/{user_id}/blogs/search")
def search_blogs(user_id: int, keyword: str, db: Session = Depends(get_db)):
    # this is a very naive version of search
    # we will modify this later.
    # for now, this will return all blogs that contain the given keyword in their content
    blogs = db.query(models.Blog).filter(models.Blog.content.contains(keyword)).all()
    return blogs

# /blogs?sort_by={criteria}&limit={n} - get top N blogs sorted by criteria 
@app.get("/blogs")
def get_top_blogs(sort_by: str, limit: int, db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).order_by(getattr(models.Blog, sort_by).desc()).limit(limit).all()
    fake_blog = blogs[0]
    fake_blogs = [fake_blog for _ in range(limit)]
    return fake_blogs

# this API will be used to update the total number of blogs published by a user
# whenever the user creates or deletes a blog.
@app.post("/{user_id}/blogs/total")
def update_total_blogs(user_id: int, n: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.total_published_blogs = n
    db.commit()
    db.refresh(user)
    return user

# things to do
# ~~1. write the APIs~~
# ~~2. setup the DB and tables~~
# ~~3. test the APIs~~
# 4. deploy the APIs with docker

# what to test?
# 1. read path - when a valid user clicked on a blog link, the blog should be displayed with title, content and the author name
# 2. write path - when a valid user publishes a blog, the blog should be saved in the DB

