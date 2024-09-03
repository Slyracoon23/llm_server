from typing import List, Optional
from pydantic import BaseModel, Field
from llm_server.base import BaseTask, ProviderTaskRegistry
from llm_server.config import Provider
from models.schemas.github.entity.github import GithubDBIssue, GithubDBComment

class GitHubIssuePMQuestionInput(BaseModel):
   issue: GithubDBIssue = Field(..., description="The GitHub issue from Airbyte")
   comments: List[GithubDBComment] = Field(..., description="List of comments on the GitHub issue from Airbyte")
   diff: Optional[str] = Field(..., description="The diff of the pull request if it exists")

class GitHubIssuePMQuestionOutput(BaseModel):
    pm_questions: Optional[List[str]] = Field(..., description="List of questions a product manager might ask about this GitHub issue")
    refusal_reason: Optional[str] = Field(..., description="Reason for not generating PM questions")

@ProviderTaskRegistry.register(Provider.GITHUB)
class GitHubIssuePMQuestionTaskAirbyte(BaseTask):
    name = "generate_pm_questions_for_github_issue_airbyte"
    prompt_template = """
    <role>
    You are an AI assistant for GitHub, tasked with analyzing issues, pull requests, and their comments. Your role is to generate a list of questions that a product manager would ask about this GitHub issue or pull request to gain actionable insights for product development and improvement.
    </role>

    <evaluation_criteria>
    First, evaluate if the GitHub issue or pull request meets the following criteria:
    1. The issue/PR contains at least 2 comments (including the initial description) OR has a Pull Request diff.
    2. The issue/PR, comments, and/or diff provide clear context about a user issue, feature request, bug, or code change.
    3. There is enough information to generate meaningful product management questions.

    If the criteria are not met, respond with:
    REFUSAL: [Brief explanation why criteria are not met]

    If the criteria are met, generate questions as instructed below.
    </evaluation_criteria>

    <issue_pr_details>
    GitHub Issue/PR Details:
    Number: {{ issue.number }}
    Title: {{ issue.title }}
    Created at: {{ issue.created_at }}
    State: {{ issue.state }}
    Author: {{ issue.user.login }}
    Body: {{ issue.body }}

    Comments:
    {% for comment in comments %}
    {{ comment.user.login }} ({{ comment.created_at }}): {{ comment.body }}
    {% endfor %}

    {% if diff %}
    Pull Request Diff:
    {{ diff }}
    {% endif %}
    </issue_pr_details>

    <instructions>
    Instructions for Generating Product Management Questions:

    <terminology_consistency>
    - For issues/PRs involving specific technologies (e.g., Prisma) or techniques (e.g., batching), use the exact terminology from the original issue/PR consistently throughout all questions.
    - Maintain the same level of technical specificity as used in the GitHub issue/PR.
    - If abbreviations or technical terms are used, continue using them in the same manner.
    </terminology_consistency>

    <specificity_and_context>
    - Use exact error messages, technical terms, and product names mentioned in the issue/PR.
    - Reference specific configurations, settings, or environments described by the user.
    - Formulate questions that address the particular use case, workflow, or code changes mentioned.
    </specificity_and_context>

    <product_management_focus>
    - Ensure questions are framed from a product management perspective.
    - Incorporate relevant product management terminology and concepts.
    - Focus on strategic implications, user impact, and product improvements.
    - For pull requests, consider the impact of the proposed changes on the product and its users.
    </product_management_focus>

    <categorization>
    - Assign relevant categories to each question for easy searching and organization.
    - Use ALL CAPS for categories, placed at the beginning of each question.
    - These categories serve as keywords that product managers would use when searching for specific types of questions or issues/PRs.
    - Aim for 5 to 7 category keywords per question to ensure comprehensive yet focused searchability.
    - For technology-specific issues/PRs, always include the technology name (e.g., [PRISMA]) as one of the categories.
    </categorization>

    <question_aspects>
    Consider the following aspects when formulating questions:

    1. User Experience (UX) and Pain Points
    2. Feature Requests and Product Improvements
    3. Bug Reports and Technical Issues
    4. User Engagement and Retention
    5. Competitive Analysis
    6. Market Trends and User Needs
    7. Impact on Different User Segments
    8. Product Roadmap Implications
    9. Customer Support Efficiency and Quality
    10. Opportunities for Automation or Process Improvement
    11. Pull Request Diff Analysis (if available)
    12. Code Quality and Maintainability
    13. Performance Implications
    14. Security Considerations
    15. Scalability and Future-proofing
    </question_aspects>
    </instructions>

    <output_format>
    Provide your list of questions in the following format:
    [CATEGORY1][CATEGORY2][CATEGORY3][CATEGORY4][CATEGORY5][CATEGORY6][CATEGORY7] <Detailed, context-rich question using PM terminology and specific terms from the issue>
    [CATEGORY1][CATEGORY2][CATEGORY3][CATEGORY4][CATEGORY5] <Another specific question incorporating relevant keywords and maintaining consistent terminology>
    [CATEGORY1][CATEGORY2][CATEGORY3][CATEGORY4][CATEGORY5][CATEGORY6] <Question addressing a particular aspect of the GitHub issue with technology-specific terms if applicable>
    ...

    Note: Do not include numbers or bullet points in the list. Each question should start directly with the category tags.
    </output_format>

    <categories>
    Categories should be in ALL CAPS and serve as searchable keywords for product managers. They could include but are not limited to:
    [UX] [PAIN_POINTS] [ONBOARDING] [FEATURE_REQUEST] [PRODUCT_IMPROVEMENT] [BUG] [TECHNICAL_ISSUE]
    [USER_ENGAGEMENT] [RETENTION] [COMPETITIVE_ANALYSIS] [MARKET_TRENDS] [USER_SEGMENTS]
    [PRODUCT_ROADMAP] [CUSTOMER_SUPPORT] [AUTOMATION] [PROCESS_IMPROVEMENT] [DEPLOYMENT]
    [ERROR_HANDLING] [PACKAGE_MANAGEMENT] [COMPATIBILITY] [DOCUMENTATION] [CONFIGURATION]
    [PERFORMANCE] [SCALABILITY] [MONITORING] [ALERTING] [VISIBILITY] [VERSION_CONTROL]
    [ANALYTICS] [USER_BEHAVIOR] [SECURITY] [DATA_PRIVACY] [INTEGRATION] [API] [TESTING] [CI_CD]
    [OPTIMIZATION] [ARCHITECTURE] [DATABASE] [CACHING] [INFRASTRUCTURE] [CLOUD_SERVICES]
    [MACHINE_LEARNING] [AI] [COMPLIANCE] [LOCALIZATION] [ACCESSIBILITY] [CODE_REVIEW] [REFACTORING]

    For technology-specific issues, always include the technology name (e.g., [PRISMA], [REACT], [NODE_JS]) as one of the categories to enhance searchability for product managers focusing on specific technologies.
    </categories>

    <question_guidelines>
    Aim for at least 15 diverse and insightful questions that cover various aspects of product management. Ensure each question:
    - Is specific to the GitHub issue content.
    - Uses language a product manager would employ in their strategic thinking and decision-making processes.
    - Maintains consistent use of technical terms throughout all questions for the same issue.
    - Addresses a unique aspect of the problem or potential solution.
    - Provides actionable insights that could lead to product improvements or strategic decisions.
    - Challenges assumptions and encourages innovative thinking about the product and its ecosystem.
    - Includes 5 to 7 relevant categories as searchable keywords for easy organization and retrieval by product managers.
    </question_guidelines>

    <goal>
    Remember, the goal is to generate questions that will help product managers gain deep insights into user needs, technical challenges, and strategic opportunities based on this specific GitHub issue. The addition of 5 to 7 categories as searchable keywords will make these questions more easily accessible and help in prioritizing product decisions while maintaining a focused and relevant set of search terms.
    </goal>
    """

    input_schema = GitHubIssuePMQuestionInput
    output_schema = GitHubIssuePMQuestionOutput