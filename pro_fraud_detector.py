import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os
import config  # <-- this is new

# --- configuration ---
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] - %(message)s')
data_file = config.data_file # <-- changed

# --- data generator (if file doesn't exist) ---
def generate_synthetic_data(num_users=10, num_transactions=1000):
    logging.info("generating synthetic data...")
    users = [f'user_{i}' for i in range(num_users)]
    local_ips = [f'192.168.1.{i}' for i in range(5)]
    risky_ips = [f'91.200.12.{i}' for i in range(5)]  # external ip addresses
    all_ips = local_ips + risky_ips

    data = []
    # create dictionaries to track the last state of each user
    last_transaction_time = {user: datetime.now() - timedelta(days=365) for user in users}
    last_ip = {user: np.random.choice(local_ips) for user in users}

    for _ in range(num_transactions):
        user = np.random.choice(users)
        
        # simulate time progression
        time_since_last = timedelta(hours=np.random.uniform(1, 200))
        timestamp = last_transaction_time[user] + time_since_last
        
        # normal transaction
        amount = np.random.lognormal(3, 1) * 10
        category = np.random.choice(['groceries', 'transport', 'bills', 'entertainment'])
        ip = last_ip[user]

        # --- inject anomalies for the detector ---
        roll = np.random.rand()
        if roll > 0.98:  # dormant account becomes active
            timestamp = last_transaction_time[user] + timedelta(days=np.random.randint(100, 200))
            amount *= 5
            logging.info(f"injecting anomaly: dormant account activity for {user}")
        elif roll > 0.95:  # ip change + large transfer
            ip = np.random.choice(risky_ips)
            amount = np.random.lognormal(5, 1) * 20
            category = 'wire_transfer'
            logging.info(f"injecting anomaly: ip change for {user}")
        elif roll > 0.92:  # risky category
            category = np.random.choice(['gambling', 'crypto_exchange'])
            amount *= 3
            logging.info(f"injecting anomaly: risky category for {user}")

        data.append([user, timestamp, amount, category, ip])
        last_transaction_time[user] = timestamp
        last_ip[user] = ip

    df = pd.DataFrame(data, columns=['user_id', 'timestamp', 'amount', 'category', 'ip_address'])
    df = df.sort_values(by='timestamp').reset_index(drop=True)
    df.to_csv(data_file, index=False)
    logging.info(f"generated and saved {len(df)} transactions to {data_file}")
    return df

def load_data():
    if os.path.exists(data_file):
        logging.info(f"loading data from {data_file}")
        df = pd.read_csv(data_file, parse_dates=['timestamp'])
        return df
    else:
        logging.warning(f"{data_file} not found.")
        return generate_synthetic_data()

# --- analysis engine ---
def analyze_transactions(df):
    logging.info("starting professional analysis...")
    df = df.sort_values(by=['user_id', 'timestamp'])
    
    # calculate time and ip differences for each user
    df['time_since_last_tx'] = df.groupby('user_id')['timestamp'].diff().dt.total_seconds() / 3600  # in hours
    df['last_ip'] = df.groupby('user_id')['ip_address'].shift(1)
    df['ip_changed'] = (df['ip_address'] != df['last_ip']) & df['last_ip'].notna()

    # --- detection rules ---
    # these are now loaded from config.py

    print("\n" + "="*80)
    print(" " * 28 + "PROFESSIONAL ANTI-FRAUD LOG")
    print("="*80 + "\n")

    alert_count = 0
    # this loop is a performance crime. we'll fix it later.
    for index, row in df.iterrows():
        alerts = []
        
        # rule 1: dormant account activity
        if pd.notna(row['time_since_last_tx']) and (row['time_since_last_tx'] / 24 > config.dormant_threshold_days): # <-- changed
            alerts.append(f"DORMANT ACCOUNT: user {row['user_id']} active after {int(row['time_since_last_tx'] / 24)} days of inactivity.")

        # rule 2: ip change + high value
        if row['ip_changed'] and row['amount'] > config.high_value_threshold: # <-- changed
            alerts.append(f"IP CHANGE: user {row['user_id']} made a large transfer (${row['amount']:.2f}) from a new ip {row['ip_address']}.")

        # rule 3: risky category
        if row['category'] in config.risky_categories: # <-- changed
            alerts.append(f"RISKY CATEGORY: transfer (${row['amount']:.2f}) from {row['user_id']} to category '{row['category']}'.")

        # rule 4: just a very large amount (less critical if no other alerts)
        if not alerts and row['amount'] > config.high_value_threshold * 1.5: # <-- changed
            alerts.append(f"LARGE AMOUNT: user {row['user_id']} made an unusually large transfer of ${row['amount']:.2f}.")

        if alerts:
            alert_count += 1
            logging.warning(f"suspicious activity detected for {row['user_id']} at {row['timestamp']}")
            print(f"[ALERT] {row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} | {alerts[0]}")
            if len(alerts) > 1:
                for extra_alert in alerts[1:]:
                    print(f"        [EXTRA] {extra_alert}")
            print(f"        [ACTION] manual review recommended. transaction id: {index}\n")
    
    print("="*80)
    if alert_count == 0:
        print(" " * 28 + "no suspicious transactions found")
    else:
        print(f" " * 25 + f"ANALYSIS COMPLETE. found {alert_count} alerts.")
    print("="*80 + "\n")

# --- entry point ---
if __name__ == "__main__":
    transactions_df = load_data()
    analyze_transactions(transactions_df)