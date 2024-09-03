import os
from fastapi import FastAPI, Path, Depends, Request, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
import logfire
from llm_server.config import Provider
from llm_server.openai_client import OpenAIClient
from llm_server.api_handler import APIHandler
from openai import OpenAI
from contextlib import asynccontextmanager
from llm_server.cache import redis_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Application:
    def __init__(self):
        self.app = FastAPI()
        self.setup_routes()
        self.setup_middleware()
        self.setup_exception_handlers()
        self.setup_logfire()

    def setup_routes(self):
        self.app.post("/api/v1/{provider}/task/{task_name}")(self.process_task)
        self.app.get("/api/v1/{provider}/tasks")(self.get_available_tasks)
        self.app.post("/api/v1/{provider}/router/{router_name}")(self.process_router)

    def setup_middleware(self):
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            logger.info(f"Incoming request: {request.method} {request.url}")
            response = await call_next(request)
            logger.info(f"Outgoing response: {response.status_code}")
            return response

    def setup_exception_handlers(self):
        @self.app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An unexpected error occurred. Please try again later."
                },
            )

    def setup_logfire(self):
        logger.info("Starting Logfire configuration")
        logfire.configure(
            token=os.getenv("LOGFIRE_TOKEN"),  # Set the token
            send_to_logfire="if-token-present",  # Only send if token is present
            scrubbing=False  # Disable scrubbing
        )
        logfire.instrument_fastapi(self.app)
        logger.info("Logfire configuration completed")

    @redis_cache()
    async def process_task(
        self,
        provider: Provider = Path(
            ..., description="The provider (github, slack, or discord)"
        ),
        task_name: str = Path(..., description="The name of the task to perform"),
        request: Dict[str, Any] = Body(..., description="The request body"),
    ) -> Dict[str, Any]:
        logger.info(f"Processing task: {provider}, {task_name}")
        client = OpenAIClient.get_client()
        return await APIHandler.process_task(provider, task_name, client, request)

    async def get_available_tasks(
        self,
        provider: Provider = Path(
            ..., description="The provider (github, slack, or discord)"
        ),
    ) -> Dict[str, Dict[str, Any]]:
        logger.info(f"Getting available tasks for provider: {provider}")
        return await APIHandler.get_available_tasks(provider)

    @redis_cache()
    async def process_router(
        self,
        provider: Provider = Path(
            ..., description="The provider (github, slack, or discord)"
        ),
        router_name: str = Path(..., description="The name of the router to process"),
        request: Dict[str, Any] = Body(..., description="The request body"),
    ) -> Dict[str, Any]:
        logger.info(f"Processing router: {provider}, {router_name}")
        client = OpenAIClient.get_client()
        return await APIHandler.process_router(provider, router_name, client, request)

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        # Setup
        logger.info("Application startup")
        yield
        # Cleanup
        logger.info("Application shutdown")

    def run(self):
        import uvicorn

        uvicorn.run(self.app, host="0.0.0.0", port=8011, lifespan="on")
