import os
from enum import Enum

class Provider(str, Enum):
    TASK = "task"
    ROUTER = "router"  # Add this line

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")