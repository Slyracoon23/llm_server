import os
from enum import Enum

class Provider(str, Enum):
    GITHUB = "github"
    SLACK = "slack"
    DISCORD = "discord"
    ROUTER = "router"  # Add this line

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")