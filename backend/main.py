from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.voice import router as voice_router
from routes.auth import router as auth_router

app = FastAPI(
    title="Veyra",
    description="Voice-to-command layer for project management software",
    version="1.0.0"
)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice_router)

@app.get("/")
def home():
    return {
        "message": "veyra is running!"
    }
    
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
    

    