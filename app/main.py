import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware as StarletteSessionMiddleware
from app.users.routes import auth_router  
from app.middleware import SessionMiddleware as CustomSessionMiddleware
from app.generate.urls import generate_router


load_dotenv() 

app = FastAPI()
app.add_middleware(StarletteSessionMiddleware, secret_key=os.getenv("SECRET_KEY", "supersecretkey"))
app.add_middleware(CustomSessionMiddleware)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(generate_router, prefix='/resume', tags=['Resume'])