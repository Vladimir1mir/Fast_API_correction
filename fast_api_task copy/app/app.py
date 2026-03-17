from fastapi import FastAPI

from .lifespan import lifespan
from .routes import router as advertisement_router


app = FastAPI(
    title="Advertisement API",
    version="0.0.1",
    description="Service for advertisements",
    lifespan=lifespan,
)

app.include_router(advertisement_router)
