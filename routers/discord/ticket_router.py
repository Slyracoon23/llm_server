from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union
from llm_server.base import BaseRouter, ProviderTaskRegistry, ProviderRouterRegistry
from llm_server.config import Provider

class GitHubIssueParams(BaseModel):
    owner: str = Field(..., description="The owner of the repository")
    repo: str = Field(..., description="The name of the repository")
    title: str = Field(..., description="The title of the issue")
    body: Optional[str] = Field(..., description="The body text of the issue")
    assignee: Optional[str] = Field(..., description="The username of the user to assign the issue to")
    milestone: Optional[str] = Field(..., description="The milestone to associate this issue with")
    labels: Optional[List[str]] = Field(..., description="A list of labels to apply to this issue")
    assignees: Optional[List[str]] = Field(..., description="A list of usernames to assign the issue to")

class GitHubIssueCommentParams(BaseModel):
    owner: str = Field(..., description="The owner of the repository")
    repo: str = Field(..., description="The name of the repository")
    issue_number: int = Field(..., description="The number of the issue to comment on")
    body: str = Field(..., description="The body text of the comment")

class LLMRouterInput(BaseModel):
    context: str = Field(..., description="context for routing decisions")
    prompt: str = Field(..., description="Prompt for routing decisions")

class LLMRouterOutput(BaseModel):
    create_issue: bool = Field(..., description="Whether to create a GitHub issue")
    create_comment: bool = Field(..., description="Whether to create a GitHub comment")
    reason: str = Field(..., description="Detailed explanation for the routing decision")
    github_issue_params: Optional[GitHubIssueParams] = Field(..., description="Parameters for creating a GitHub issue")
    github_issue_comment_params: Optional[GitHubIssueCommentParams] = Field(..., description="Parameters for creating a GitHub issue comment")

@ProviderRouterRegistry.register(Provider.DISCORD)
class SupportTicketLLMRouter(BaseRouter):
    name = "support_ticket_router"
    instruction_template = """
    You are an AI assistant tasked with routing requests to create GitHub issues and/or comments based on the provided context and prompt.
    Please determine whether to create a GitHub issue, create a GitHub comment, both, or neither based on the context and messages.
    
    If you decide to create an issue or comment, you must provide the necessary parameters.
    """
    context_template = """
    Context:
    {{ context }}
    """
    format_instructions = """
    Format your response as follows:
    Create Issue: <true/false>
    Create Comment: <true/false>
    Reason: <detailed explanation for your decision>
    
    If Create Issue is true, include:
    GitHub Issue Parameters:
    - owner: <repository owner>
    - repo: <repository name>
    - title: <issue title>
    - body: <issue body>
    - assignee: <assignee username> (optional)
    - milestone: <milestone number or title> (optional)
    - labels: <list of labels> (optional)
    - assignees: <list of assignee usernames> (optional)
    
    If Create Comment is true, include:
    GitHub Comment Parameters:
    - owner: <repository owner>
    - repo: <repository name>
    - issue_number: <issue number>
    - body: <comment body>
    """
    prompt_template = """
    Prompt:
    {{ prompt }}
    """
    input_schema = LLMRouterInput
    output_schema = LLMRouterOutput