import importlib
import os

def load_tasks():
    task_dir = os.path.join(os.path.dirname(__file__), 'tasks')
    for provider in os.listdir(task_dir):
        provider_dir = os.path.join(task_dir, provider)
        if os.path.isdir(provider_dir):
            for task_file in os.listdir(provider_dir):
                if task_file.endswith('.py'):
                    module_name = f"llm_server.tasks.{provider}.{task_file[:-3]}"
                    importlib.import_module(module_name)
                    
                    

def load_routers():
    router_dir = os.path.join(os.path.dirname(__file__), 'routers')
    for provider in os.listdir(router_dir):
        provider_dir = os.path.join(router_dir, provider)
        if os.path.isdir(provider_dir):
            for router_file in os.listdir(provider_dir):
                if router_file.endswith('.py'):
                    module_name = f"llm_server.routers.{provider}.{router_file[:-3]}"
                    importlib.import_module(module_name)