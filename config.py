import os
from enum import Enum

class Provider(str, Enum):
    SUMMARIZATION = "summarization"
    MODERATION = "moderation"

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")