from typing import List
from pydantic import BaseModel, Field
from llm_server.base import BaseTask, ProviderTaskRegistry
from llm_server.config import Provider
from models.schemas.github.entity.github import PullRequest, PullRequestComment

class GitHubPRSummarizationInput(BaseModel):
    pull_request: PullRequest = Field(..., description="The main pull request details")
    comments: List[PullRequestComment] = Field(..., description="List of comments on the pull request")

class GitHubPRSummarizationOutput(BaseModel):
    summary: str = Field(..., description="A concise summary of the pull request and its comments")
    key_points: List[str] = Field(..., description="A list of key points extracted from the pull request and comments")
    suggested_reviewers: List[str] = Field(..., description="A list of suggested reviewers based on the content")
    estimated_complexity: str = Field(..., description="Estimated complexity of the PR: Low, Medium, or High")
    potential_conflicts: List[str] = Field(..., description="Potential conflicts or issues identified in the PR")
    next_steps: List[str] = Field(..., description="Suggested next steps for the PR")

    class Config:
        schema_extra = {
            "example": {
                "summary": "This PR implements a new feature for user authentication using OAuth2.",
                "key_points": [
                    "Adds OAuth2 authentication flow",
                    "Implements new user model",
                    "Updates API endpoints for auth",
                ],
                "suggested_reviewers": ["@security-team", "@backend-lead"],
                "estimated_complexity": "Medium",
                "potential_conflicts": [
                    "May conflict with ongoing database schema changes",
                    "Potential security implications need thorough review",
                ],
                "next_steps": [
                    "Conduct security review",
                    "Update documentation",
                    "Plan for integration testing",
                ],
            }
        }

@ProviderTaskRegistry.register(Provider.GITHUB)
class GitHubPRSummarizationTask(BaseTask):
    name = "summarize_pr"
    prompt_template = """
    You are an AI assistant for GitHub, tasked with summarizing pull request details and comments. Your role is to provide a concise and informative summary of the pull request discussion.
    Pull Request Details:
    Title: {{ pull_request.title }}
    Number: #{{ pull_request.number }}
    State: {{ pull_request.state }}
    Created by: {{ pull_request.user.login }}
    Created at: {{ pull_request.created_at }}
    Comments:
    {% for comment in comments %}
    {{ comment.user.login }} ({{ comment.created_at }}): {{ comment.body }}
    {% endfor %}
    Please provide a summary of the pull request and its comments, highlighting the main points of discussion, suggested reviewers, estimated complexity, potential conflicts, and next steps.
    Provide your analysis using the following format:
    Summary: <concise summary of the pull request and its comments>
    Key Points: <list of key points extracted from the pull request and comments>
    Suggested Reviewers: <list of suggested reviewers based on the content>
    Estimated Complexity: <estimated complexity of the PR: Low, Medium, or High>
    Potential Conflicts: <list of potential conflicts or issues identified in the PR>
    Next Steps: <list of suggested next steps for the PR>
    """

    input_schema = GitHubPRSummarizationInput
    output_schema = GitHubPRSummarizationOutput