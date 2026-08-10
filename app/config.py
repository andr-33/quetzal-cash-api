import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PORT = os.getenv('PORT')
    DEBUG = os.getenv('FLASK_DEBUG', "False") == "True"
    GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIAL_FILE')
    GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')