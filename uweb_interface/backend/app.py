from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uweb_interface.backend.routes import router

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
