import os
from typing import Optional


class TemplateLoader:
    def __init__(self, template_path: Optional[str] = None):
        if template_path and not os.path.exists(template_path):
            raise FileNotFoundError(f"Email template file not found: {template_path}")
        self.template_path = template_path

    def render(self, recipient_name: str, receiver_name: str, message: str = '', gift_limit: str = '$100') -> str:
        if not self.template_path:
            raise ValueError("No template path provided")
        
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        html = template_content.replace('{recipient_name}', recipient_name)
        html = html.replace('{receiver_name}', receiver_name)
        html = html.replace('{gift_limit}', gift_limit)
        
        if message:
            message_html = f'<div style="background-color: #fff9e6; border-left: 4px solid #ff9800; padding: 15px; margin: 20px 0; border-radius: 4px;"><p style="margin: 0; font-style: italic; color: #333;">{message}</p></div>'
            html = html.replace('{custom_message}', message_html)
        else:
            html = html.replace('{custom_message}', '')
        
        return html

