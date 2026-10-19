from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os

from routes.auth import router as auth_router
from routes.scan import router as scan_router
from routes.chat import router as chat_router
from routes.admin import router as admin_router

app = FastAPI(title="Document Analysis API")

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(SessionMiddleware, secret_key=os.getenv("JWT_SECRET", "secret"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(scan_router)
app.include_router(chat_router)
app.include_router(admin_router)

@app.get("/")
def read_root():
    return {"message": "Document Analysis API is running", "status": "ok"}

