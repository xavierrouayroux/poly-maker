# Poly-Maker

A market making bot for Polymarket prediction markets. This bot automates the process of providing liquidity to markets on Polymarket by maintaining orders on both sides of the book with configurable parameters.

## Overview

Poly-Maker is a comprehensive solution for automated market making on Polymarket. It includes:

- Real-time order book monitoring via WebSockets
- Position management with risk controls
- Customizable trade parameters fetched from Google Sheets
- Automated position merging functionality
- Sophisticated spread and price management

## Structure

The repository consists of several interconnected modules:

- `poly_data`: Core data management and market making logic
- `poly_merger`: Utility for merging positions (based on open-source Polymarket code)
- `poly_stats`: Account statistics tracking
- `poly_utils`: Shared utility functions
- `data_updater`: Separate module for collecting market information

## Requirements

- Python 3.8+
- Node.js (for poly_merger)
- Google Sheets API credentials
- Polymarket account and API credentials

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/poly-maker.git
cd poly-maker
```

2. Install Python dependencies:
```
pip install -r requirements.txt
```

3. Install Node.js dependencies for the merger:
```
cd poly_merger
npm install
cd ..
```

4. Set up your environment variables by copying the example file:
```
cp .env.example .env
```

5. Edit the `.env` file with your credentials:
- `PK`: Your private key for Polymarket
- `BROWSER_ADDRESS`: Your wallet address
- `SPREADSHEET_URL`: URL to your Google Sheets configuration

6. Create a Google Service Account and download credentials:
```
cp data_updater/credentials.json.example credentials.json
```
Edit the credentials.json with your Google service account details.

## Configuration

The bot is configured via a Google Spreadsheet with several worksheets:

- **Selected Markets**: Markets you want to trade
- **All Markets**: Database of all markets on Polymarket
- **Hyperparameters**: Configuration parameters for the trading logic

## Usage

### Data Collection

Before running the main bot, you need to gather market data:

```
cd data_updater
python find_markets.py
```

This will populate your Google Sheet with available markets.

### Running the Bot

Start the market maker:

```
python main.py
```

The bot will:
1. Connect to Polymarket API
2. Subscribe to market data via WebSockets
3. Place and manage orders according to your configuration
4. Monitor and merge positions when beneficial

## Notes on poly_merger

The `poly_merger` module is a particularly powerful utility that handles position merging on Polymarket. It's built on open-source Polymarket code and provides a smooth way to consolidate positions, reducing gas fees and improving capital efficiency.

## Important Notes

- This code interacts with real markets and can potentially lose real money
- Test thoroughly with small amounts before deploying with significant capital
- The `data_updater` is technically a separate repository but is included here for convenience
- The `find_markets.py` script in the data_updater is essential for the bot to get market information

## License

MIT