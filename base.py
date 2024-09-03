from abc import ABC, abstractmethod
from typing import Dict, Any, Type, ClassVar, List
from pydantic import BaseModel
from openai import AsyncOpenAI
from llm_server.config import Provider
from llm_server.template_renderer import TemplateRenderer
from llm_server.openai_client import OpenAIClient

class TaskOutput(BaseModel):
    action_type: str
    action_data: Dict[str, Any]
    action_embedding: List[float]

class BaseTask(ABC):
    name: ClassVar[str]
    prompt_template: ClassVar[str]
    input_schema: ClassVar[Type[BaseModel]]
    output_schema: ClassVar[Type[BaseModel]]

    @classmethod
    async def process(cls, client: AsyncOpenAI, input_data: Dict[str, Any]) -> Dict[str, Any]:
        validated_input = cls.input_schema(**input_data)
        prompt = TemplateRenderer.render(cls.prompt_template, **validated_input.model_dump())
        print(prompt)
        response_output = await OpenAIClient.completion(client, prompt, cls.output_schema)
        
        output_json = response_output.model_dump_json()
        embedding = await OpenAIClient.generate_embedding(client, output_json)
        
        return TaskOutput(
            action_type=cls.name,
            action_data=response_output.model_dump(),
            action_embedding=embedding
        ).model_dump()

class ProviderTaskRegistry:
    _providers: Dict[Provider, Dict[str, Type[BaseTask]]] = {provider: {} for provider in Provider}

    @classmethod
    def register(cls, provider: Provider):
        def decorator(task_class: Type[BaseTask]):
            cls._providers[provider][task_class.name] = task_class
            return task_class
        return decorator

    @classmethod
    def get_task(cls, provider: Provider, task_name: str) -> Type[BaseTask]:
        provider_tasks = cls._providers.get(provider)
        if not provider_tasks:
            raise ValueError(f"Unknown provider: {provider}")
        task = provider_tasks.get(task_name)
        if not task:
            raise ValueError(f"Unknown task type for provider {provider}: {task_name}")
        return task

    @classmethod
    def get_available_tasks(cls, provider: Provider) -> List[str]:
        return list(cls._providers[provider].keys())
    
class RouterOutput(BaseModel):
    router_type: str
    router_data: Dict[str, Any]
    router_embedding: List[float]
    
class BaseRouter(ABC):
    name: ClassVar[str]
    instruction_template: ClassVar[str]
    context_template: ClassVar[str]
    format_instructions: ClassVar[str]
    prompt_template: ClassVar[str]
    input_schema: ClassVar[Type[BaseModel]]
    output_schema: ClassVar[Type[BaseModel]]
    
    @classmethod
    async def process(cls, client: AsyncOpenAI, input_data: Dict[str, Any]) -> Dict[str, Any]:
        validated_input = cls.input_schema(**input_data)
        
        templates = {
            'instructions': cls.instruction_template,
            'context': cls.context_template,
            'format_instructions': cls.format_instructions,
            'prompt': cls.prompt_template,
        }
        
        rendered = {key: TemplateRenderer.render(template, **validated_input.model_dump())
                    for key, template in templates.items()}
        
        response_output = await OpenAIClient.router_call(
            client,
            instructions=rendered['instructions'],
            context=rendered['context'],
            format_instructions=rendered['format_instructions'],
            prompt=rendered['prompt'],
            response_format=cls.output_schema
        )
        
        output_json = response_output.model_dump_json()
        embedding = await OpenAIClient.generate_embedding(client, output_json)
    
        return RouterOutput(
            router_type=cls.name,
            router_data=response_output.model_dump(),
            router_embedding=embedding
        ).model_dump()

    
class ProviderRouterRegistry:
    _providers: Dict[Provider, Dict[str, Type[BaseRouter]]] = {provider: {} for provider in Provider}
    
    @classmethod
    def register(cls, provider: Provider):
        def decorator(task_class: Type[BaseRouter]):
            cls._providers[provider][task_class.name] = task_class
            return task_class
        return decorator
    
    @classmethod
    def get_router(cls, provider: Provider, router_name: str) -> Type[BaseRouter]:
        provider_routers = cls._providers.get(provider)
        if not provider_routers:
            raise ValueError(f"Unknown provider: {provider}")
        router = provider_routers.get(router_name)
        if not router:
            raise ValueError(f"Unknown router type for provider {provider}: {router_name}")
        return router
    
    
    @classmethod
    def get_available_routers(cls, provider: Provider) -> List[str]:
        return list(cls._providers[provider].keys())