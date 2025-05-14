from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.routes import api_router 

app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
