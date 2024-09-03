from typing import List, Optional
from pydantic import BaseModel, Field
from llm_server.base import BaseTask, ProviderTaskRegistry
from llm_server.config import Provider
from models.schemas.discord.entity.discord import DiscordMessagesThread, DiscordThreads
from models.schemas.github.entity.github import GithubDBIssue

class GitHubIssueCommentParams(BaseModel):
    owner: str = Field(..., description="The owner of the repository")
    repo: str = Field(..., description="The name of the repository")
    issue_number: int = Field(..., description="The number of the issue to comment on")
    body: str = Field(..., description="The body text of the comment")

class DiscordGitHubCommentTaskInputAirbyte(BaseModel):
    channel: DiscordThreads = Field(..., description="The Discord channel of the support ticket")
    messages: List[DiscordMessagesThread] = Field(..., description="List of messages in the support ticket channel")
    github_issues: List[GithubDBIssue] = Field(..., description="List of github issues in github")

class DiscordGitHubCommentTaskOutputAirbyte(BaseModel):
    create_comment: bool = Field(..., description="Whether to create a GitHub issue comment")
    github_comment_params: Optional[GitHubIssueCommentParams] = Field(..., description="Parameters for creating a GitHub issue comment")
    refusal_reason: Optional[str] = Field(..., description="Reason for not creating a GitHub issue comment")

@ProviderTaskRegistry.register(Provider.DISCORD)
class DiscordGitHubCommentTaskAirbyte(BaseTask):
    name = "create_github_comment_task_airbyte"
    prompt_template = """
    You are an AI assistant for Discord, tasked with analyzing support ticket channels and deciding whether to create a GitHub issue comment based on the content. Your role is to determine if the support ticket warrants adding a comment to an existing GitHub issue and, if so, to provide the necessary parameters for creating the comment.

    First, evaluate if the support ticket meets the following criteria for creating a GitHub issue comment:
    1. The ticket contains relevant information related to an existing GitHub issue.
    2. The information provides updates, additional context, or new insights about the issue.
    3. The comment would add value to the existing GitHub issue discussion.

    If the criteria are not met, respond with:
    <refusal>
    [Brief explanation why criteria are not met]
    </refusal>

    If the criteria are met, generate the GitHub issue comment parameters as instructed below.

    <support_ticket_details>
    Channel ID: {{ channel.id }}
    Channel Name: {{ channel.name }}
    Created at: {{ channel.thread_metadata.create_timestamp }}
    Messages:
    {% for message in messages %}
    {{ message.author.username }} ({{ message.timestamp }}): {{ message.content }}
    {% endfor %}
    </support_ticket_details>

    <existing_github_issues>
    {% for issue in github_issues %}
    <issue>
    <number>{{ issue.number }}</number>
    <title>{{ issue.title }}</title>
    <body>{{ issue.body }}</body>
    </issue>
    {% endfor %}
    </existing_github_issues>

    Instructions for Creating GitHub Issue Comment Parameters:

    1. Issue Number:
       - Identify the most relevant existing GitHub issue to comment on.

    2. Body:
       - Provide a clear and concise comment that adds value to the existing issue.
       - Include relevant information from the support ticket, such as new observations, updates, or additional context.
       - Use markdown formatting to improve readability (e.g., code blocks, bullet points).

    Output Format:
    Provide your decision and GitHub issue comment parameters in the following format:

    <create_comment>true/false</create_comment>
    <reason>[Brief explanation for your decision]</reason>

    If create_comment is true, include:
    <github_comment_params>
    <owner>airbytehq</owner>
    <repo>airbyte</repo>
    <issue_number>[Number of the relevant issue]</issue_number>
    <body>
    [Detailed comment in markdown format]
    </body>
    </github_comment_params>

    Remember, the goal is to add valuable comments to existing GitHub issues that will help the development team address important bugs, feature requests, or user problems efficiently. Make sure to reference the existing GitHub issues to find the most relevant one for your comment.
    """

    input_schema = DiscordGitHubCommentTaskInputAirbyte
    output_schema = DiscordGitHubCommentTaskOutputAirbyte