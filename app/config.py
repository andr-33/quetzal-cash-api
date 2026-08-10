import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PORT = os.getenv('PORT')
    DEBUG = os.getenv('FLASK_DEBUG', "False") == "True"