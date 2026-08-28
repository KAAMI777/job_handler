import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
frontend_url = os.getenv("VERCEL_URL")
origins= ["http://localhost:5173/" , frontend_url]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/health")
def health():
    return {"status": "pramit its working fine bro"}