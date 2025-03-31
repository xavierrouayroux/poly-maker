# Polymarket Market Maker Data Updater

This tool analyzes Polymarket prediction markets to identify profitable market making opportunities. It fetches market data, calculates potential rewards, analyzes price volatility, and updates a Google Spreadsheet with the results.

## Features

- Fetches all available Polymarket markets
- Calculates rewards based on market maker formulas
- Analyzes price volatility over different time windows
- Updates Google Sheets with market opportunities sorted by profitability
- Automatically runs every 5 minutes

## Prerequisites

- Python 3.7+
- A Google Cloud project with Sheets API enabled
- Polymarket account with an API key

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your private key (see example below)
4. Create a Google service account and download `credentials.json`
5. Set up your Google Spreadsheet with the following worksheets:
   - "All Markets"
   - "Volatility Markets"
   - "Full Markets"
   - "Selected Markets"

## Running the Tool

```
python update_markets.py
```

This will start the continuous update process, refreshing market data every 5 minutes.

## Configuration Files

### .env Example

```
PK=your_polygon_wallet_private_key
SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/your_spreadsheet_id/edit
```

### credentials.json Example

This is a Google service account credentials file. Create one at the [Google Cloud Console](https://console.cloud.google.com/):

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project-id.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
}
```

## Security Notes

- Keep your private key and credentials.json secure
- Never commit sensitive files to public repositories
- Use environment variables for sensitive information

## Disclaimer

This tool is for educational purposes only. Trading cryptocurrency involves significant risk. This is not financial advice.