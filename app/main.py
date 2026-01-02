from fastapi import FastAPI
from app.database import models
from app.database.session import engine
from .api.v1 import auth
from .api.v1 import products

app = FastAPI(
    title="Skincare Tracker API",
    description="Backend API untuk monitoring rutin skincare dengan integrasi AI",
    version="1.0.0"
)

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {
        "message": "Welcome to Skincare Tracker API!",
        "status": "Server is running and Database is connected"
    }

app.include_router(auth.router)
app.include_router(products.router)