from jinja2 import Template

class TemplateRenderer:
    @staticmethod
    def render(template: str, **kwargs) -> str:
        return Template(template).render(**kwargs)
    
    
    