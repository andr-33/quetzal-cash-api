import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_sheets_client(config):
    credentials = Credentials.from_service_account_file(
        config["GOOGLE_SHEETS_CREDENTIALS"],
        scopes=SCOPES
    )
    return gspread.authorize(credentials) 