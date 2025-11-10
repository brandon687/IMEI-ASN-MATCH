import os
import json
import gspread
from google.oauth2.service_account import Credentials

def get_google_sheets_client():
    """Get authenticated gspread client using service account credentials"""
    # Check for service account credentials in environment variable
    google_creds_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')

    if not google_creds_json:
        raise Exception(
            'GOOGLE_SHEETS_CREDENTIALS environment variable not found. '
            'Please set it with your service account JSON credentials.'
        )

    try:
        # Parse the JSON credentials
        creds_dict = json.loads(google_creds_json)

        # Define the required scopes
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        # Create credentials from service account info
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)

        # Authorize and return the client
        client = gspread.authorize(credentials)

        return client

    except json.JSONDecodeError as e:
        raise Exception(f'Invalid JSON in GOOGLE_SHEETS_CREDENTIALS: {str(e)}')
    except Exception as e:
        raise Exception(f'Error authenticating with Google Sheets: {str(e)}')
