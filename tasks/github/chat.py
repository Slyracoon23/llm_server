from pydantic import create_model
from typing import List, Optional, Dict
from llm_server.base import BaseTask, ProviderTaskRegistry
from llm_server.config import Provider

@ProviderTaskRegistry.register(Provider.GITHUB)
class GitHubChatTask(BaseTask):
    name = "chat"
    prompt_template = """
    You are an AI assistant for GitHub, a developer support platform. Your role is to provide helpful and consistent support across multiple interactions, maintaining context throughout the conversation.

    Context:
    {% if context %}
    {% for context_item in context %}
    {{ context_item }}
    {% endfor %}
    {% else %}
    No context available.
    {% endif %}

    Chat History:
    {% for message in messages %}
    {{ message.role }}: {{ message.content }}
    {% endfor %}

    Please provide a helpful response to the user's latest message, taking into account the entire conversation history. Your response should be informative, friendly, and tailored to the user's needs.

    Provide your analysis using the following format:
    Response: <your response to the user's latest message>
    Reason: <explanation of your response, including how it relates to the conversation history>
    Title: <concise summary of the current state of the conversation>
    """

    input_schema = create_model(
        'GitHubChatInput',
        context=(Optional[List[str]], None),
        messages=(List[Dict[str, str]], ...)
    )

    output_schema = create_model(
        'GitHubChatOutput',
        response=(str, ...),
        reason=(str, ...),
        title=(str, ...)
    )