import logging
from fastapi import FastAPI
from src import models
from src.utils.uvicorn_filters import HealthCheckFilter
from src.routers import healthcheck_api, document_api
from src.database import engine

# Hide healthcheck logs from uvicorn access logs
logging.getLogger("uvicorn.access").addFilter(HealthCheckFilter())


# Initialize the FastAPI app
app = FastAPI(title="Rimal-AI Backend API's", version="1.0.0")

# creting all models
models.Base.metadata.create_all(engine)

app.include_router(router=healthcheck_api.router, prefix="/healthz")
app.include_router(router=document_api.router, prefix="/document")
