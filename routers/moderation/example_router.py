from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union
from base import BaseRouter, ProviderTaskRegistry, ProviderRouterRegistry
from config import Provider

class ContentModerationParams(BaseModel):
    content_id: str = Field(..., description="Unique identifier for the content")
    content_type: str = Field(..., description="Type of content (e.g., text, image, video)")
    content: str = Field(..., description="The content to be moderated")
    reason: str = Field(..., description="Reason for the moderation decision")
    action: str = Field(..., description="Action to be taken (e.g., flag, remove, approve)")

class LLMRouterInput(BaseModel):
    context: str = Field(..., description="Context for moderation decisions")
    prompt: str = Field(..., description="Content to be moderated")

class LLMRouterOutput(BaseModel):
    flag_content: bool = Field(..., description="Whether to flag the content for review")
    approve_content: bool = Field(..., description="Whether to approve the content")
    reason: str = Field(..., description="Detailed explanation for the moderation decision")
    flag_params: Optional[ContentModerationParams] = Field(None, description="Parameters for flagging content")
    approve_params: Optional[ContentModerationParams] = Field(None, description="Parameters for approving content")

@ProviderRouterRegistry.register(Provider.MODERATION)
class ContentModerationRouter(BaseRouter):
    name = "content_moderation_router"
    instruction_template = """
    You are an AI assistant tasked with content moderation. Based on the provided context and prompt, determine whether to flag the content for review or approve it directly.
    Consider factors such as hate speech, explicit content, violence, harassment, and misinformation when making your decision.
    """
    context_template = """
    Context:
    {{ context }}
    """
    format_instructions = """
    Format your response as follows:
    Flag Content: <true/false>
    Approve Content: <true/false>
    Reason: <detailed explanation for your decision>
    
    If Flag Content is true, include:
    Flag Parameters:
    - content_id: <unique identifier for the content>
    - content_type: <type of content>
    - content: <the content being moderated>
    - reason: <reason for flagging>
    - action: <suggested action (e.g., "review", "remove")>
    
    If Approve Content is true, include:
    Approve Parameters:
    - content_id: <unique identifier for the content>
    - content_type: <type of content>
    - content: <the content being moderated>
    - reason: <reason for approval>
    - action: "approve"
    """
    prompt_template = """
    Content to moderate:
    {{ prompt }}
    """
    input_schema = LLMRouterInput
    output_schema = LLMRouterOutput