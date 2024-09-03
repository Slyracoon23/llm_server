from pydantic import create_model, Field
from typing import List, Optional
from llm_server.base import BaseTask, ProviderTaskRegistry
from llm_server.config import Provider

@ProviderTaskRegistry.register(Provider.SLACK)
class SlackKeywordExtractionTask(BaseTask):
    name = "extract_keywords"
    prompt_template = """
    You are an AI assistant helping to extract important keywords from Slack messages.

    Context:
    {% if context %}
    {% for context_item in context %}
    {{ context_item }}
    {% endfor %}
    {% else %}
    No context available.
    {% endif %}

    Messages:
    {% for message in messages %}
    {{ message }}
    {% endfor %}

    Please extract the most important keywords from the messages above.

    Provide your analysis using the following format:
    Keywords: <keyword1>, <keyword2>, ..., <keyword10>
    Reason: <detailed explanation for choosing each keyword, with specific examples from the messages>
    Title: <concise summary of how the keywords relate to the main topics or themes>
    """

    input_schema = create_model(
        'SlackKeywordExtractionInput',
        context=(Optional[List[str]], None),
        messages=(List[str], ...)
    )

    output_schema = create_model(
        'SlackKeywordExtractionOutput',
        keywords=(List[str], Field(..., min_items=1, max_items=10)),
        reason=(str, ...),
        title=(str, ...)
    )