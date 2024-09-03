from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from models.schemas.slack.entity.slack import SlackMessage
from llm_server.base import BaseTask, ProviderTaskRegistry
from llm_server.config import Provider

class SlackMessageSummarizationInput(BaseModel):
    message: SlackMessage

class SlackMessageSummarizationOutput(BaseModel):
    summary: str = Field(..., description="A concise summary of the Slack message")
    keywords: List[str] = Field(..., description="A list of keywords extracted from the message")
    sentiment: str = Field(..., description="The sentiment of the message (positive, negative, or neutral)")
    importance: int = Field(..., description="Importance score of the message (1-5)")
    action_items: Optional[List[str]] = Field(description="List of action items extracted from the message, if any")
    thread_type: Optional[str] = Field(description="The type of thread (e.g., question, announcement, discussion)")

@ProviderTaskRegistry.register(Provider.SLACK)
class SlackMessageSummarizationTask(BaseTask):
    name = "summarize_message"
    prompt_template = """
    You are an AI assistant for Slack, tasked with summarizing messages. Your role is to provide a concise and informative summary of a Slack message, including its key points and potential action items.

    Message Details:
    Sender: {{ message.user_id }}
    Timestamp: {{ message.timestamp }}
    Channel: {{ message.channel_id }}
    Content: {{ message.text }}

    Please analyze the message and provide the following information:
    Summary: <concise summary of the message>
    Keywords: <list of keywords extracted from the message>
    Sentiment: <sentiment of the message: positive, negative, or neutral>
    Importance: <importance score of the message from 1 to 5>
    Action Items: <list of action items extracted from the message, if any>
    Thread Type: <type of thread, e.g., question, announcement, discussion>

    Provide your analysis using the following format:
    Summary: <summary>
    Keywords: <keyword1>, <keyword2>, <keyword3>
    Sentiment: <sentiment>
    Importance: <importance_score>
    Action Items: <action_item1>, <action_item2>
    Thread Type: <thread_type>
    """

    input_schema = SlackMessageSummarizationInput
    output_schema = SlackMessageSummarizationOutput