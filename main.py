from llm_server.application import Application
from llm_server.loaders import load_tasks, load_routers
from llm_server.base import ProviderTaskRegistry, ProviderRouterRegistry

if __name__ == "__main__":
    load_tasks()
    load_routers()
    print(ProviderTaskRegistry._providers)  # Debug print
    print(ProviderRouterRegistry._providers)  # Debug print
    app = Application()
    app.run()