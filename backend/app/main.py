from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.api import router as api_router

def get_application() -> FastAPI:
    application = FastAPI()

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix="/api")

    return application

app = get_application()