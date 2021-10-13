import json

class Json:
    def __init__(self):
        self.config_file = "config/config.json"

    def token(self):
        with open(self.config_file, 'r') as f:
            item = json.load(f)
        return item["token"]

    def prefix(self):
        with open(self.config_file, 'r') as f:
            item = json.load(f)
        return item["prefix"]

class Config:
    def __init__(self):
        self.token = Json.token()
        self.prefix = Json.prefix()