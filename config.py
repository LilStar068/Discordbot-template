import os
import dotenv

dotenv.load_dotenv(".env")


class Config:
    def __init__(self):
        self.token = os.environ.get("TOKEN")
        self.prefix = os.environ.get("PREFIX")
        self.owner_id = [696650928907878440]
