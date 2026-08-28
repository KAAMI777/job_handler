import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# frontend_url = os.getenv("FRONTEND_URL")

origins = [
    "http://localhost:5173",
    "https://job-handler-4aoavbxig-kaami777.vercel.app",
    "https://job-handler.vercel.app/"
]

# if frontend_url:
#     origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}