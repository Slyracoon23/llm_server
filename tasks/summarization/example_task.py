from typing import List, Optional
from pydantic import BaseModel, Field
from base import BaseTask, ProviderTaskRegistry
from config import Provider

class SummaryParams(BaseModel):
    title: str = Field(..., description="A concise title for the summary")
    summary: str = Field(..., description="The main summary text")
    key_points: List[str] = Field(..., description="A list of key points from the content")
    categories: Optional[List[str]] = Field(None, description="Relevant categories or tags")

class SummarizationTaskInput(BaseModel):
    content: str = Field(..., description="The content to be summarized")
    max_length: Optional[int] = Field(None, description="Maximum length of the summary")
    focus_areas: Optional[List[str]] = Field(None, description="Specific areas to focus on in the summary")

class SummarizationTaskOutput(BaseModel):
    summary_params: SummaryParams = Field(..., description="Parameters for the generated summary")

@ProviderTaskRegistry.register(Provider.SUMMARIZATION)
class GenericSummarizationTask(BaseTask):
    name = "generic_summarization_task"
    prompt_template = """
    You are an AI assistant tasked with summarizing content. Your role is to analyze the given content and provide a concise summary along with key points and relevant categories.

    Content to summarize:
    {{ content }}

    {% if max_length %}
    Maximum summary length: {{ max_length }} characters
    {% endif %}

    {% if focus_areas %}
    Focus areas:
    {% for area in focus_areas %}
    - {{ area }}
    {% endfor %}
    {% endif %}

    Instructions for Creating Summary Parameters:

    1. Title:
       - Create a concise, descriptive title that captures the main idea of the content.

    2. Summary:
       - Provide a clear and concise summary of the content.
       - Highlight the most important information and main ideas.
       - Ensure the summary is coherent and well-structured.

    3. Key Points:
       - Identify and list the most important points from the content.
       - Aim for 3-5 key points, unless the content complexity requires more.

    4. Categories:
       - Suggest relevant categories or tags that best describe the content.
       - These can be general themes, topics, or domains related to the content.

    Output Format:
    Provide your summary in the following format:

    <summary_params>
    <title>[Concise, descriptive title]</title>
    <summary>
    [Clear and concise summary of the content]
    </summary>
    <key_points>
    - [Key point 1]
    - [Key point 2]
    - [Key point 3]
    ...
    </key_points>
    <categories>
    - [Category 1]
    - [Category 2]
    ...
    </categories>
    </summary_params>

    Remember, the goal is to create an informative and concise summary that captures the essence of the given content. Focus on the most important information and ensure that your summary is easy to understand.
    """

    input_schema = SummarizationTaskInput
    output_schema = SummarizationTaskOutput