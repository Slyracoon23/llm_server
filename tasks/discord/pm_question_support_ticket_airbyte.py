from typing import List, Optional
from pydantic import BaseModel, Field
from llm_server.base import BaseTask, ProviderTaskRegistry
from llm_server.config import Provider
from models.schemas.discord.entity.discord import DiscordMessagesThread,  DiscordThreads

class DiscordSupportTicketInputAirbyte(BaseModel):
    channel:  DiscordThreads = Field(..., description="The Discord channel of the support ticket")
    messages: List[DiscordMessagesThread] = Field(..., description="List of messages in the support ticket channel")

class DiscordSupportTicketOutputAirbyte(BaseModel):
    pm_questions: Optional[List[str]] = Field(..., description="List of questions a product manager might ask about this support ticket")
    refusal_reason: Optional[str] = Field(..., description="Reason for not generating PM questions")

@ProviderTaskRegistry.register(Provider.DISCORD)
class DiscordSupportTicketPMQuestionTaskAirbyte(BaseTask):
    name = "generate_pm_questions_for_support_ticket_airbyte"
    prompt_template = """
    You are an AI assistant for Discord, tasked with analyzing support ticket channels. Your role is to generate a list of questions that a product manager would ask about this support ticket to gain actionable insights for product development and improvement.

    First, evaluate if the support ticket meets the following criteria:
    1. The ticket contains at least 3 messages.
    2. The messages provide clear context about a user issue, feature request, or bug.
    3. There is enough information to generate meaningful product management questions.

    If the criteria are not met, respond with:
    REFUSAL: [Brief explanation why criteria are not met]

    If the criteria are met, generate questions as instructed below.

    Support Ticket Details:
    Channel ID: {{ channel.id }}
    Channel Name: {{ channel.name }}
    Created at: {{ channel.thread_metadata.create_timestamp }}
    Messages:
    {% for message in messages %}
    {{ message.author.username }} ({{ message.timestamp }}): {{ message.content }}
    {% endfor %}

    Instructions for Generating Product Management Questions:

    1. Terminology Consistency:
       - For issues involving specific technologies (e.g., Prisma) or techniques (e.g., batching), use the exact terminology from the original issue consistently throughout all questions.
       - Maintain the same level of technical specificity as used in the support ticket.
       - If abbreviations or technical terms are used, continue using them in the same manner.

    2. Specificity and Context:
       - Use exact error messages, technical terms, and product names mentioned in the ticket.
       - Reference specific configurations, settings, or environments described by the user.
       - Formulate questions that address the particular use case or workflow mentioned.

    3. Product Management Focus:
       - Ensure questions are framed from a product management perspective.
       - Incorporate relevant product management terminology and concepts.
       - Focus on strategic implications, user impact, and product improvements.

    4. Categorization:
       - Assign relevant categories to each question for easy searching and organization.
       - Use ALL CAPS for categories, placed at the beginning of each question.
       - These categories serve as keywords that product managers would use when searching for specific types of questions or issues.
       - Aim for 5 to 7 category keywords per question to ensure comprehensive yet focused searchability.
       - For technology-specific issues, always include the technology name (e.g., [PRISMA]) as one of the categories.

    Consider the following aspects when formulating questions:

    1. User Experience (UX) and Pain Points:
       - User journey, friction points, usability issues
       - Onboarding process, feature discoverability
       - Accessibility concerns, platform-specific problems

    2. Feature Requests and Product Improvements:
       - Feature prioritization, product backlog
       - User stories, use cases, job-to-be-done
       - MVP (Minimum Viable Product) considerations

    3. Bug Reports and Technical Issues:
       - Severity and priority of bugs
       - Reproducibility, edge cases, platform dependencies
       - Technical debt, scalability concerns

    4. User Engagement and Retention:
       - User activation, core product value
       - Engagement metrics, retention rates, churn factors
       - Feature adoption, user segmentation

    5. Competitive Analysis:
       - Unique selling proposition (USP), feature parity
       - Competitor strengths and weaknesses
       - Market positioning, differentiation strategy

    6. Market Trends and User Needs:
       - Emerging technologies, industry shifts
       - User behavior patterns, demographic insights
       - Long-term vision, product-market fit

    7. Impact on Different User Segments:
       - Persona-specific issues, use case variations
       - Enterprise vs. individual user needs
       - Geographical or cultural considerations

    8. Product Roadmap Implications:
       - Release planning, feature dependencies
       - Resource allocation, development sprints
       - OKRs (Objectives and Key Results), KPIs (Key Performance Indicators)

    9. Customer Support Efficiency and Quality:
       - First response time, time to resolution
       - Self-service options, knowledge base improvements
       - Support ticket categorization, escalation processes

    10. Opportunities for Automation or Process Improvement:
        - Workflow optimization, integration possibilities
        - AI/ML implementation, chatbot enhancements
        - Data-driven decision making, A/B testing

    Output Format:
    Provide your list of questions in the following format:
    [CATEGORY1][CATEGORY2][CATEGORY3][CATEGORY4][CATEGORY5][CATEGORY6][CATEGORY7] <Detailed, context-rich question using PM terminology and specific terms from the ticket>
    [CATEGORY1][CATEGORY2][CATEGORY3][CATEGORY4][CATEGORY5] <Another specific question incorporating relevant keywords and maintaining consistent terminology>
    [CATEGORY1][CATEGORY2][CATEGORY3][CATEGORY4][CATEGORY5][CATEGORY6] <Question addressing a particular aspect of the support ticket with technology-specific terms if applicable>
    ...

    Note: Do not include numbers or bullet points in the list. Each question should start directly with the category tags.

    Categories should be in ALL CAPS and serve as searchable keywords for product managers. They could include but are not limited to:
    [UX] [PAIN_POINTS] [ONBOARDING] [FEATURE_REQUEST] [PRODUCT_IMPROVEMENT] [BUG] [TECHNICAL_ISSUE]
    [USER_ENGAGEMENT] [RETENTION] [COMPETITIVE_ANALYSIS] [MARKET_TRENDS] [USER_SEGMENTS]
    [PRODUCT_ROADMAP] [CUSTOMER_SUPPORT] [AUTOMATION] [PROCESS_IMPROVEMENT] [DEPLOYMENT]
    [ERROR_HANDLING] [PACKAGE_MANAGEMENT] [COMPATIBILITY] [DOCUMENTATION] [CONFIGURATION]
    [PERFORMANCE] [SCALABILITY] [MONITORING] [ALERTING] [VISIBILITY] [VERSION_CONTROL]
    [ANALYTICS] [USER_BEHAVIOR] [SECURITY] [DATA_PRIVACY] [INTEGRATION] [API] [TESTING] [CI_CD]
    [OPTIMIZATION] [ARCHITECTURE] [DATABASE] [CACHING] [INFRASTRUCTURE] [CLOUD_SERVICES]
    [MACHINE_LEARNING] [AI] [COMPLIANCE] [LOCALIZATION] [ACCESSIBILITY]

    For technology-specific issues, always include the technology name (e.g., [PRISMA], [REACT], [NODE_JS]) as one of the categories to enhance searchability for product managers focusing on specific technologies.

    Aim for at least 15 diverse and insightful questions that cover various aspects of product management. Ensure each question:
    - Is specific to the support ticket content.
    - Uses language a product manager would employ in their strategic thinking and decision-making processes.
    - Maintains consistent use of technical terms throughout all questions for the same issue.
    - Addresses a unique aspect of the problem or potential solution.
    - Provides actionable insights that could lead to product improvements or strategic decisions.
    - Challenges assumptions and encourages innovative thinking about the product and its ecosystem.
    - Includes 5 to 7 relevant categories as searchable keywords for easy organization and retrieval by product managers.

    Remember, the goal is to generate questions that will help product managers gain deep insights into user needs, technical challenges, and strategic opportunities based on this specific support ticket. The addition of 5 to 7 categories as searchable keywords will make these questions more easily accessible and help in prioritizing product decisions while maintaining a focused and relevant set of search terms.
    """

    input_schema = DiscordSupportTicketInputAirbyte
    output_schema = DiscordSupportTicketOutputAirbyte