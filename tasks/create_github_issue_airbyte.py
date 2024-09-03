from typing import List, Optional
from pydantic import BaseModel, Field
from llm_server.base import BaseTask, ProviderTaskRegistry
from llm_server.config import Provider
from models.schemas.discord.entity.discord import DiscordMessagesThread, DiscordThreads
from models.schemas.github.entity.github import GithubDBIssue

class GitHubIssueParams(BaseModel):
    owner: str = Field(..., description="The owner of the repository")
    repo: str = Field(..., description="The name of the repository")
    title: str = Field(..., description="The title of the issue")
    body: str = Field(..., description="The body text of the issue")
    assignee: Optional[str] = Field(..., description="The username of the user to assign the issue to")
    milestone: Optional[str] = Field(..., description="The milestone to associate this issue with")
    labels: Optional[List[str]] = Field(..., description="A list of labels to apply to this issue")
    assignees: Optional[List[str]] = Field(..., description="A list of usernames to assign the issue to")

class DiscordGitHubTaskInputAirbyte(BaseModel):
    channel: DiscordThreads = Field(..., description="The Discord channel of the support ticket")
    messages: List[DiscordMessagesThread] = Field(..., description="List of messages in the support ticket channel")
    github_issues: List[GithubDBIssue] = Field(..., description="List of github issues in github" )

class DiscordGitHubTaskOutputAirbyte(BaseModel):
    create_issue: bool = Field(..., description="Whether to create a GitHub issue")
    github_issue_params: Optional[GitHubIssueParams] = Field(..., description="Parameters for creating a GitHub issue")
    refusal_reason: Optional[str] = Field(..., description="Reason for not creating a GitHub issue")

@ProviderTaskRegistry.register(Provider.DISCORD)
class DiscordGitHubTaskAirbyte(BaseTask):
    name = "create_github_task_airbyte"
    prompt_template = """
    You are an AI assistant for Discord, tasked with analyzing support ticket channels and deciding whether to create a GitHub issue based on the content. Your role is to determine if the support ticket warrants creating a GitHub issue and, if so, to provide the necessary parameters for creating the issue.

    First, evaluate if the support ticket meets the following criteria for creating a GitHub issue:
    1. The ticket contains information about a bug, feature request, or significant user problem.
    2. The issue is not a simple question that can be answered without developer intervention.
    3. The problem described is not already known or documented.
    4. There is enough information to create a meaningful GitHub issue.

    If the criteria are not met, respond with:
    <refusal>
    [Brief explanation why criteria are not met]
    </refusal>

    If the criteria are met, generate the GitHub issue parameters as instructed below.

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
    <title>{{ issue.title }}</title>
    <body>{{ issue.body }}</body>
    </issue>
    {% endfor %}
    </existing_github_issues>

    Instructions for Creating GitHub Issue Parameters:

    1. Title:
       - Create a concise, descriptive title that summarizes the main issue or request.
       - Use prefixes like [BUG], [FEATURE], or [IMPROVEMENT] to categorize the issue.

    2. Body:
       - Provide a detailed description of the issue or request.
       - Include relevant information from the support ticket, such as steps to reproduce, expected vs. actual behavior, and any error messages.
       - Use markdown formatting to improve readability (e.g., code blocks, bullet points).

    3. Labels:
       - Assign appropriate labels based on the nature of the issue (e.g., bug, enhancement, documentation).
       - Include priority labels if the urgency is clear from the support ticket.

    4. Assignees:
       - If specific team members or experts are mentioned in the ticket, include them as assignees.

    5. Milestone:
       - If the issue aligns with a known milestone or release, specify it.

    Output Format:
    Provide your decision and GitHub issue parameters in the following format:

    <create_issue>true/false</create_issue>
    <reason>[Brief explanation for your decision]</reason>

    If create_issue is true, include:
    <github_issue_params>
    <owner>airbytehq</owner>
    <repo>airbyte</repo>
    <title>[Concise, descriptive title]</title>
    <body>
    [Detailed issue description in markdown format]
    </body>
    <labels>[List of relevant labels]</labels>
    <assignees>[List of relevant assignees, if any]</assignees>
    <milestone>[Milestone name, if applicable]</milestone>
    </github_issue_params>

    Remember, the goal is to create meaningful GitHub issues that will help the development team address important bugs, feature requests, or user problems efficiently. Make sure to check the existing GitHub issues to avoid creating duplicates.
    """

    input_schema = DiscordGitHubTaskInputAirbyte
    output_schema = DiscordGitHubTaskOutputAirbyte