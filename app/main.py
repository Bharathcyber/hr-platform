from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.employees import router as employees_router

app = FastAPI(
    title="HR Platform API",
    description="Backend API for the HR Platform.",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(employees_router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "HR Platform API is running"}