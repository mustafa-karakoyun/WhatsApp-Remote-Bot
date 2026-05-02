import os
import yaml
import random
from typing import Dict, List, Tuple

def ensure_directory(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

def load_config(config_path: str) -> dict:
    default_config = {
        'logging': {'level': 'INFO', 'console_enabled': True, 'file_enabled': False},
        'browser': {'profile_path': './whatsapp_profile', 'headless': False, 'window_size': '1920,1080'},
        'messaging': {'timeouts': {'element_wait': 20, 'qr_scan': 60}},
        'security': {
            'rate_limiting': {'max_messages_per_hour': 10, 'max_messages_per_day': 50, 'cooldown_after_limit': 3600},
            'human_simulation': {'enabled': True, 'typing_delay_min': 0.1, 'typing_delay_max': 0.3, 'message_delay_min': 1, 'message_delay_max': 3}
        },
        'advanced': {'media': {'enabled': True, 'max_file_size_mb': 50, 'allowed_types': ['.jpg', '.png', '.pdf', '.jpeg', '.avif', '.mp4']}, 'reporting': {'enabled': False, 'output_directory': './reports', 'formats': ['txt'], 'include_statistics': False}},
        'reporting': {'enabled': False, 'output_directory': './reports', 'formats': ['txt'], 'include_statistics': False}
    }
    if not os.path.exists(config_path):
        return default_config
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_templates() -> dict:
    return {'templates': {}}

def render_template(template_name: str, variables: dict, templates: dict) -> str:
    return f"Template {template_name} rendered with {variables}"



def parse_recipients(recipients_str: str) -> List[str]:
    if not recipients_str: return []
    return [r.strip() for r in recipients_str.split(',') if r.strip()]

def validate_media_file(file_path: str, max_size_mb: int, allowed_types: list) -> Tuple[bool, str]:
    if not os.path.exists(file_path):
        return False, "Dosya bulunamadı"
    return True, "Valid"

def random_delay(min_d: float, max_d: float) -> float:
    return random.uniform(min_d, max_d)

class MessageStats:
    def __init__(self):
        self.success_count = 0
        self.failure_count = 0
        self.success_numbers = []
        self.failure_numbers = []

    def add_success(self, phone: str):
        self.success_count += 1
        self.success_numbers.append(phone)

    def add_failure(self, phone: str):
        self.failure_count += 1
        self.failure_numbers.append(phone)

    def to_dict(self) -> dict:
        return {
            'success': self.success_count,
            'failed': self.failure_count
        }