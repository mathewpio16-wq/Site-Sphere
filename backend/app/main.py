from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.users import router as users_router
from app.api.notifications import router as notification_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="sitesphere API",
    description="Backend API for the SiteSphere construction collaboration platform",
    version="1.0.0",
    openapi_version="3.0.3",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(notification_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to SiteSphere API"
    }