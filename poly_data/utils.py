import json
from poly_utils.google_utils import get_spreadsheet
import pandas as pd 
import os

def pretty_print(txt, dic):
    print("\n", txt, json.dumps(dic, indent=4))

def get_sheet_df(read_only=None):
    """
    Get sheet data with optional read-only mode
    
    Args:
        read_only (bool): If None, auto-detects based on credentials availability
    """
    all = 'All Markets'
    sel = 'Selected Markets'

    # Auto-detect read-only mode if not specified
    if read_only is None:
        creds_file = 'credentials.json' if os.path.exists('credentials.json') else '../credentials.json'
        read_only = not os.path.exists(creds_file)
        if read_only:
            print("No credentials found, using read-only mode")

    try:
        spreadsheet = get_spreadsheet(read_only=read_only)
    except FileNotFoundError:
        print("No credentials found, falling back to read-only mode")
        spreadsheet = get_spreadsheet(read_only=True)

    wk = spreadsheet.worksheet(sel)
    df = pd.DataFrame(wk.get_all_records())
    df = df[df['question'] != ""].reset_index(drop=True)

    wk2 = spreadsheet.worksheet(all)
    df2 = pd.DataFrame(wk2.get_all_records())
    df2 = df2[df2['question'] != ""].reset_index(drop=True)

    result = df.merge(df2, on='question', how='inner')

    wk_p = spreadsheet.worksheet('Hyperparameters')
    records = wk_p.get_all_records()
    hyperparams, current_type = {}, None

    for r in records:
        current_type = r['type'] or current_type
        hyperparams.setdefault(current_type, {})[r['param']] = r['value']

    return result, hyperparams
