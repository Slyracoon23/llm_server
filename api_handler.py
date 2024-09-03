import asyncio
from typing import Dict, Any
from fastapi import HTTPException
from openai import AsyncOpenAI
from config import Provider
from base import ProviderTaskRegistry, ProviderRouterRegistry
from openai_client import OpenAIClient

class APIHandler:
    @staticmethod
    async def process_task(
        provider: Provider,
        task_name: str,
        client: AsyncOpenAI,
        request: Dict[str, Any]
    ) ->  Dict[str, Any]:
        try:
            task_class = ProviderTaskRegistry.get_task(provider, task_name)
            return await task_class.process(client, request)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        
    @staticmethod
    async def process_router(
        provider: Provider,
        router_name: str,
        client: AsyncOpenAI,
        request: Dict[str, Any]
    ) ->  Dict[str, Any]:
        try:
            router_class = ProviderRouterRegistry.get_router(provider, router_name)
            return await router_class.process(client, request)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def get_available_tasks(provider: Provider) -> Dict[str, Dict[str, Any]]:
        tasks = ProviderTaskRegistry.get_available_tasks(provider)
        task_details = {}
        for task_name in tasks:
            task_class = ProviderTaskRegistry.get_task(provider, task_name)
            task_details[task_name] = {
                "name": task_class.name,
                "prompt_template": task_class.prompt_template,
                "input_schema": task_class.input_schema.schema(),
                "output_schema": task_class.output_schema.schema(),
            }
        return task_details