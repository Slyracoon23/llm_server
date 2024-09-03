# LLM Server

LLM Server is a FastAPI-based application that provides a flexible and extensible framework for handling various AI tasks using Large Language Models (LLMs). It supports multiple providers and can be easily extended with new tasks and routers.

## Features

- Support for multiple providers
- Extensible task and router system
- Redis caching for improved performance
- OpenAI integration for LLM-based tasks
- Logging with Logfire integration

## Project Structure

- `application.py`: Main FastAPI application setup
- `cache.py`: Redis caching implementation
- `openai_client.py`: OpenAI client wrapper
- `main.py`: Entry point for the application
- `tasks/`: Directory containing task implementations for different providers
- `routers/`: Directory containing router implementations

## Key Components

1. **BaseTask**: Abstract base class for defining tasks
2. **BaseRouter**: Abstract base class for defining routers
3. **ProviderTaskRegistry**: Registry for managing tasks across providers
4. **ProviderRouterRegistry**: Registry for managing routers across providers
5. **OpenAIClient**: Wrapper for the OpenAI API client
6. **Application**: Main FastAPI application class

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/llm-server.git
   cd llm-server
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   export OPENAI_API_KEY=your_openai_api_key
   export REDIS_URL=redis://localhost:6379
   export LOGFIRE_TOKEN=your_logfire_token
   ```

4. Run the server:
   ```
   python main.py
   ```

## Usage

The server exposes the following endpoints:

- `POST /api/v1/{provider}/task/{task_name}`: Execute a specific task for a provider
- `GET /api/v1/{provider}/tasks`: Get available tasks for a provider
- `POST /api/v1/{provider}/router/{router_name}`: Process a router for a provider

## Example Task

Here's an example of how to create a new task:

## Adding New Tasks

To add a new task:

1. Create a new Python file in the `tasks/` directory
2. Define a new class that inherits from `BaseTask`
3. Implement the required methods and properties
4. Register the task using the `@ProviderTaskRegistry.register(Provider.PROVIDER_NAME)` decorator

## Adding New Routers

To add a new router:

1. Create a new Python file in the appropriate provider directory under `routers/`
2. Define a new class that inherits from `BaseRouter`
3. Implement the required methods and properties
4. Register the router using the `@ProviderRouterRegistry.register(Provider.PROVIDER_NAME)` decorator

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.