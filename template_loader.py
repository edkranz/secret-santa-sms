import os
from typing import Optional


class TemplateLoader:
    def __init__(self, template_path: Optional[str] = None):
        if template_path and not os.path.exists(template_path):
            raise FileNotFoundError(f"Email template file not found: {template_path}")
        self.template_path = template_path

    def render(self, recipient_name: str, receiver_name: str) -> str:
        if not self.template_path:
            raise ValueError("No template path provided")
        
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        html = template_content.replace('{recipient_name}', recipient_name)
        html = html.replace('{receiver_name}', receiver_name)
        
        return html

