import os
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import Type, List
from llm_server.config import Config
import logfire  # Add this import


class OpenAIClient:
    @staticmethod
    def get_client():
        client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        logfire.configure(
            token=os.getenv("LOGFIRE_TOKEN"),  # Set the token
            send_to_logfire="if-token-present",  # Only send if token is present
        )  # Configure Logfire
        logfire.instrument_openai(client)  # Instrument the OpenAI client
        return client

    @staticmethod
    async def completion(
        client: AsyncOpenAI, prompt: str, response_format: Type[BaseModel]
    ) -> BaseModel:
        response = await client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt},
            ],
            response_format=response_format,
        )
        parsed_response = response.choices[0].message.parsed
        if parsed_response is None:
            raise ValueError("Failed to parse response")
        return parsed_response

    @staticmethod
    async def router_call(
        client: AsyncOpenAI,
        instructions: str,
        context: str,
        format_instructions: str,
        prompt: str,
        response_format: Type[BaseModel],
    ) -> BaseModel:
        response = await client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "system", "content": instructions},
                {"role": "system", "content": context},
                {"role": "system", "content": format_instructions},
                {"role": "user", "content": prompt},
            ],
            response_format=response_format,
        )
        parsed_response = response.choices[0].message.parsed
        if parsed_response is None:
            raise ValueError("Failed to parse response")
        return parsed_response

    @staticmethod
    async def generate_embedding(client: AsyncOpenAI, text: str) -> List[float]:
        response = await client.embeddings.create(
            model="text-embedding-3-large", input=text
        )
        return response.data[0].embedding
