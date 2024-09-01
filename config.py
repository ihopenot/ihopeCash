from typing import Dict
import yaml

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.load(f, Loader=yaml.FullLoader)

Config: Dict = load_config()