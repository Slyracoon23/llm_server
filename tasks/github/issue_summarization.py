from typing import List
from pydantic import BaseModel, Field
from llm_server.base import BaseTask, ProviderTaskRegistry
from llm_server.config import Provider
from models.schemas.github.entity.github import GitHubUser, Issue, IssueComment

class GitHubIssueSummarizationInput(BaseModel):
    issue: Issue = Field(..., description="The main issue details")
    comments: List[IssueComment] = Field(..., description="List of comments on the issue")

class GitHubIssueSummarizationOutput(BaseModel):
    summary: str = Field(..., description="Concise summary of the issue and its comments")
    key_points: List[str] = Field(..., description="List of key points discussed")
    decisions: List[str] = Field(..., description="List of decisions made or action items")
    current_status: str = Field(..., description="Current status of the issue based on the comments")

@ProviderTaskRegistry.register(Provider.GITHUB)
class GitHubIssueSummarizationTask(BaseTask):
    name = "summarize_issue"
    prompt_template = """
    You are an AI assistant for GitHub, tasked with summarizing issue comments. Your role is to provide a concise and informative summary of the discussion in a GitHub issue.
    Issue Details:
    Title: {{ issue.title }}
    Number: #{{ issue.number }}
    State: {{ issue.state }}
    Created by: {{ issue.user.login }}
    Created at: {{ issue.created_at }}
    Comments:
    {% for comment in comments %}
    {{ comment.user.login }} ({{ comment.created_at }}): {{ comment.body }}
    {% endfor %}
    Please provide a summary of the issue and its comments, highlighting the main points of discussion, any decisions made, and the current status of the issue.
    Provide your analysis using the following format:
    Summary: <concise summary of the issue and its comments>
    Key Points: <list of key points discussed>
    Decisions: <any decisions made or action items>
    Current Status: <current status of the issue based on the comments>
    """

    input_schema = GitHubIssueSummarizationInput
    output_schema = GitHubIssueSummarizationOutput