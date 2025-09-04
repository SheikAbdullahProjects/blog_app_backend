from fastapi import FastAPI, HTTPException
from database import Base, engine
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from auth import auth_routes
from blog import blog_routes
from review import review_routes

load_dotenv()

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Blog Application",
    description="Blog Application with User Authentication and Reviews",
    version="0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def check_app():
    return {
        "detail" : "Working Fine"
    }
    
app.include_router(auth_routes.router)
app.include_router(blog_routes.router)
app.include_router(review_routes.router)