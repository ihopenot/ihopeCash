from typing import Dict
import yaml

def load_config():
    with open('config.yaml', 'r', encoding="utf-8") as f:
        return yaml.load(f, Loader=yaml.FullLoader)

Config: Dict = load_config()