import pandas as pd
import numpy as np
import os
import requests
import time
import warnings
warnings.filterwarnings("ignore")


if not os.path.exists('data'):
    os.makedirs('data')

def get_sel_df(spreadsheet, sheet_name='Selected Markets'):
    try:
        wk2 = spreadsheet.worksheet(sheet_name)
        sel_df = pd.DataFrame(wk2.get_all_records())
        sel_df = sel_df[sel_df['question'] != ""].reset_index(drop=True)
        return sel_df
    except:
        return pd.DataFrame()
    
def get_all_markets(client):
    cursor = ""
    all_markets = []

    while True:
        try:
            markets = client.get_sampling_markets(next_cursor = cursor)
            markets_df = pd.DataFrame(markets['data'])


            cursor = markets['next_cursor']
            


            all_markets.append(markets_df)

            if cursor is None:
                break
        except:
            break

    all_df = pd.concat(all_markets)
    all_df = all_df.reset_index(drop=True)

    return all_df

def get_bid_ask_range(ret, TICK_SIZE):
    bid_from = ret['midpoint'] - ret['max_spread'] / 100
    bid_to = ret['best_ask'] #Although bid to this high up will change bid_from because of changing midpoint, take optimistic approach

    if bid_to == 0:
        bid_to = ret['midpoint']

    if bid_to - TICK_SIZE > ret['midpoint']:
        bid_to = ret['best_bid'] + (TICK_SIZE + 0.1 * TICK_SIZE)

    if bid_from > bid_to:
        bid_from = bid_to - (TICK_SIZE + 0.1 * TICK_SIZE)

    ask_to = ret['midpoint'] + ret['max_spread'] / 100
    ask_from = ret['best_bid']

    if ask_from == 0:
        ask_from = ret['midpoint']

    if ask_from + TICK_SIZE < ret['midpoint']:
        ask_from = ret['best_ask'] - (TICK_SIZE + 0.1 * TICK_SIZE)

    if ask_from > ask_to:
        ask_to = ask_from + (TICK_SIZE + 0.1 * TICK_SIZE)

    bid_from = round(bid_from, 3)
    bid_to = round(bid_to, 3)
    ask_from = round(ask_from, 3)
    ask_to = round(ask_to, 3)

    if bid_from < 0:
        bid_from = 0

    if ask_from < 0:
        ask_from = 0
        
    return bid_from, bid_to, ask_from, ask_to


def generate_numbers(start, end, TICK_SIZE):
    # Calculate the starting point, rounding up to the next hundredth if not an exact multiple of TICK_SIZE
    rounded_start = (int(start * 100) + 1) / 100 if start * 100 % 1 != 0 else start + TICK_SIZE
    
    # Calculate the ending point, rounding down to the nearest hundredth
    rounded_end = int(end * 100) / 100
    
    # Generate numbers from rounded_start to rounded_end, ensuring they fall strictly within the original bounds
    numbers = []
    current = rounded_start
    while current < end:
        numbers.append(current)
        current += TICK_SIZE
        current = round(current, len(str(TICK_SIZE).split('.')[1]))  # Rounding to avoid floating point imprecision

    return numbers

def add_formula_params(curr_df, midpoint, v, daily_reward):
    curr_df['s'] = (curr_df['price'] - midpoint).abs()
    curr_df['S'] = ((v - curr_df['s']) / v) ** 2
    curr_df['100'] = 1/curr_df['price'] * 100

    curr_df['size'] = curr_df['size'] + curr_df['100']

    curr_df['Q'] = curr_df['S'] * curr_df['size']
    curr_df['reward_per_100'] = (curr_df['Q'] / curr_df['Q'].sum()) * daily_reward / 2 / curr_df['size'] * curr_df['100']
    return curr_df

def process_single_row(row, client):
    ret = {}
    ret['question'] = row['question']
    ret['neg_risk'] = row['neg_risk']

    ret['answer1'] = row['tokens'][0]['outcome']
    ret['answer2'] = row['tokens'][1]['outcome']

    ret['min_size'] = row['rewards']['min_size']
    ret['max_spread'] = row['rewards']['max_spread']

    token1 = row['tokens'][0]['token_id']
    token2 = row['tokens'][1]['token_id']

    rate = 0
    for rate_info in row['rewards']['rates']:
        if rate_info['asset_address'].lower() == '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'.lower():
            rate = rate_info['rewards_daily_rate']
            break

    ret['rewards_daily_rate'] = rate
    book = client.get_order_book(token1)
    
    bids = pd.DataFrame()
    asks = pd.DataFrame()

    try:
        bids = pd.DataFrame(book.bids).astype(float)
    except:
        pass

    try:
        asks = pd.DataFrame(book.asks).astype(float)
    except:
        pass


    try:
        ret['best_bid'] = bids.iloc[-1]['price']
    except:
        ret['best_bid'] = 0

    try:
        ret['best_ask'] = asks.iloc[-1]['price']
    except:
        ret['best_ask'] = 0

    ret['midpoint'] = (ret['best_bid'] + ret['best_ask']) / 2
    
    TICK_SIZE = row['minimum_tick_size']
    ret['tick_size'] = TICK_SIZE

    bid_from, bid_to, ask_from, ask_to = get_bid_ask_range(ret, TICK_SIZE)
    v = round((ret['max_spread'] / 100), 2)

    bids_df = pd.DataFrame()
    bids_df['price'] = generate_numbers(bid_from, bid_to, TICK_SIZE)

    asks_df = pd.DataFrame()
    asks_df['price'] = generate_numbers(ask_from, ask_to, TICK_SIZE)

    try:
        bids_df = bids_df.merge(bids, on='price', how='left').fillna(0)
    except:
        bids_df = pd.DataFrame()

    try:
        asks_df = asks_df.merge(asks, on='price', how='left').fillna(0)
    except:
        asks_df = pd.DataFrame()

    best_bid_reward = 0
    ret_bid = pd.DataFrame()

    try:
        ret_bid = add_formula_params(bids_df, ret['midpoint'], v, rate)
        best_bid_reward = round(ret_bid['reward_per_100'].max(), 2)
    except:
        pass

    best_ask_reward = 0
    ret_ask = pd.DataFrame()

    try:
        ret_ask = add_formula_params(asks_df, ret['midpoint'], v, rate)
        best_ask_reward = round(ret_ask['reward_per_100'].max(), 2)
    except:
        pass

    ret['bid_reward_per_100'] = best_bid_reward
    ret['ask_reward_per_100'] = best_ask_reward

    ret['sm_reward_per_100'] = round((best_bid_reward + best_ask_reward) / 2, 2)
    ret['gm_reward_per_100'] = round((best_bid_reward * best_ask_reward) ** 0.5, 2)

    ret['end_date_iso'] = row['end_date_iso']
    ret['market_slug'] = row['market_slug']
    ret['token1'] = token1
    ret['token2'] = token2
    ret['condition_id'] = row['condition_id']

    return ret


def get_all_results(all_df, client, max_workers=3, batch_size=40):
    all_results = []

    def process_with_progress(args):
        idx, row = args
        try:
            return process_single_row(row, client)
        except:
            print("error fetching market")
            return None

    # Process in batches to respect rate limits (Book endpoint: 50 requests/10s)
    for i in range(0, len(all_df), batch_size):
        batch_df = all_df.iloc[i:i+batch_size]
        batch_results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_with_progress, (idx, row)) for idx, row in batch_df.iterrows()]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result is not None:
                    batch_results.append(result)
        
        all_results.extend(batch_results)
        print(f'{len(all_results)} of {len(all_df)} markets processed')
        
        # Rate limit: sleep for 10 seconds after each batch to respect API limits
        if i + batch_size < len(all_df):
            print("Waiting 10 seconds to respect rate limits...")
            time.sleep(10)

    return all_results

def get_combined_markets(new_df, new_markets, sel_df):

    if len(sel_df) > 0:
        old_markets = new_df[new_df['question'].isin(sel_df['question'])]
        all_markets = pd.concat([old_markets, new_markets])
    else:
        all_markets = new_markets

    all_markets = all_markets.drop_duplicates('question')

    all_markets = all_markets.sort_values('gm_reward_per_100', ascending=False)
    return all_markets

import concurrent.futures

def calculate_annualized_volatility(df, hours):
    end_time = df['t'].max()
    start_time = end_time - pd.Timedelta(hours=hours)
    window_df = df[df['t'] >= start_time]
    volatility = window_df['log_return'].std()
    annualized_volatility = volatility * np.sqrt(60 * 24 * 252)
    return round(annualized_volatility, 2)

def add_volatility(row):
    res = requests.get(f'https://clob.polymarket.com/prices-history?interval=1m&market={row["token1"]}&fidelity=10')
    price_df = pd.DataFrame(res.json()['history'])
    price_df['t'] = pd.to_datetime(price_df['t'], unit='s')
    price_df['p'] = price_df['p'].round(2)

    price_df.to_csv(f'data/{row["token1"]}.csv', index=False)
    
    price_df['log_return'] = np.log(price_df['p'] / price_df['p'].shift(1))

    row_dict = row.copy()

    stats = {
        '1_hour': calculate_annualized_volatility(price_df, 1),
        '3_hour': calculate_annualized_volatility(price_df, 3),
        '6_hour': calculate_annualized_volatility(price_df, 6),
        '12_hour': calculate_annualized_volatility(price_df, 12),
        '24_hour': calculate_annualized_volatility(price_df, 24),
        '7_day': calculate_annualized_volatility(price_df, 24 * 7),
        '14_day': calculate_annualized_volatility(price_df, 24 * 14),
        '30_day': calculate_annualized_volatility(price_df, 24 * 30),
        'volatility_price': price_df['p'].iloc[-1]
    }

    new_dict = {**row_dict, **stats}
    return new_dict

def add_volatility_to_df(df, max_workers=2, batch_size=40):
    
    results = []
    df = df.reset_index(drop=True)

    def process_volatility_with_progress(args):
        idx, row = args
        try:
            ret = add_volatility(row.to_dict())
            return ret
        except:
            print("Error fetching volatility")
            return None

    # Process in batches to respect rate limits (Price endpoint: 100 requests/10s)
    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i:i+batch_size]
        batch_results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_volatility_with_progress, (idx, row)) for idx, row in batch_df.iterrows()]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result is not None:
                    batch_results.append(result)
        
        results.extend(batch_results)
        print(f'{len(results)} of {len(df)} volatility calculations completed')

        # Rate limit: sleep for 10 seconds after each batch to respect API limits
        if i + batch_size < len(df):
            print("Waiting 10 seconds to respect rate limits...")
            time.sleep(10)
            
    return pd.DataFrame(results)

    
def get_markets(all_results, sel_df, maker_reward=1):
    new_df = pd.DataFrame(all_results)
    new_df['spread'] = abs(new_df['best_ask'] - new_df['best_bid'])
    new_df = new_df.sort_values('rewards_daily_rate', ascending=False)
    new_df[' '] = ''

    new_df = new_df[['question', 'answer1', 'answer2', 'neg_risk', 'spread', 'best_bid', 'best_ask', 'rewards_daily_rate', 'bid_reward_per_100', 'ask_reward_per_100', 'gm_reward_per_100', 'sm_reward_per_100', 'min_size', 'max_spread', 'tick_size', 'market_slug', 'token1', 'token2', 'condition_id']]
    new_df = new_df.replace([np.inf, -np.inf], 0)
    all_data = new_df.copy()
    s_df = new_df.copy()
    

    making_markets = s_df[~new_df['question'].isin(sel_df['question'])]
    making_markets = making_markets.sort_values('gm_reward_per_100', ascending=False)
    making_markets = making_markets[making_markets['gm_reward_per_100'] >= maker_reward]
    all_markets = get_combined_markets(new_df, making_markets, sel_df)    

    return all_data, all_markets
