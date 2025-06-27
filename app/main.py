from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from ai import *
import os

load_dotenv()

app = FastAPI()

def get_api_url():
    return os.getenv("TEST_API_URL") if os.getenv("API_TYPE") == "test" else os.getenv("PRODUCTION_API_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_api_url()],
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.get("/")
async def root():
    return {"status": "healthy"}
