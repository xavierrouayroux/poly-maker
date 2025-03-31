import json
from poly_utils.google_utils import get_spreadsheet
import pandas as pd 

def pretty_print(txt, dic):
    print("\n", txt, json.dumps(dic, indent=4))

def get_sheet_df():

    all = 'All Markets'
    sel = 'Selected Markets'

    spreadsheet = get_spreadsheet()

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
