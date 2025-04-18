from google.oauth2.service_account import Credentials
import gspread
import os
from dotenv import load_dotenv

load_dotenv()

def get_spreadsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    creds_file = 'credentials.json' if os.path.exists('credentials.json') else '../credentials.json'
    credentials = Credentials.from_service_account_file(creds_file, scopes=scope)
    client = gspread.authorize(credentials)
    spreadsheet_url = os.getenv("SPREADSHEET_URL")
    if not spreadsheet_url:
        raise ValueError("SPREADSHEET_URL environment variable is not set")

    spreadsheet = client.open_by_url(spreadsheet_url)
    return spreadsheet


