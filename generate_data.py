import pandas as pd
import numpy as np
from faker import Faker
from datetime import timedelta

# --- config ---
num_records = 1000
output_file = 'transactions.csv'
dormancy_threshold = 30  # must match config.py
risky_categories = ['online_gambling', 'crypto_exchange', 'adult_services']  # must match config.py
suspicious_ips = ['138.197.10.1', '104.248.60.2', '64.227.100.5']  # must match config.py

# --- setup ---
fake = Faker()
print("generating mock transaction data...")

# --- data generation ---
data = []
for i in range(num_records):
    user_id = fake.uuid4()
    last_login = fake.date_time_between(start_date='-1y', end_date='now')
    
    # ~10% chance of a "suspicious" transaction
    is_alert_candidate = np.random.choice([True, False], p=[0.1, 0.9])
    
    if is_alert_candidate:
        fraud_type = np.random.choice(['dormancy', 'category', 'ip'])
        if fraud_type == 'dormancy':
            last_login = fake.date_time_between(start_date='-2y', end_date='-1y')
            transaction_time = last_login + timedelta(days=np.random.randint(dormancy_threshold + 5, 365))
            category = 'electronics'
            ip = fake.ipv4()
        elif fraud_type == 'category':
            transaction_time = last_login + timedelta(days=np.random.randint(1, 5))
            category = np.random.choice(risky_categories)
            ip = fake.ipv4()
        else:  # ip
            transaction_time = last_login + timedelta(days=np.random.randint(1, 5))
            category = 'groceries'
            ip = np.random.choice(suspicious_ips)
    else:
        # normal transaction
        transaction_time = last_login + timedelta(days=np.random.randint(1, 5))
        category = np.random.choice(['groceries', 'restaurants', 'utilities', 'shopping', 'transport'])
        ip = fake.ipv4()

    data.append({
        'transaction_id': i + 1,
        'user_id': user_id,
        'amount': round(np.random.uniform(5.0, 2500.0), 2),
        'transaction_date': transaction_time,
        'last_login_date': last_login,
        'transaction_category': category,
        'ip_address': ip
    })

df = pd.DataFrame(data)
# format dates for consistency
df['transaction_date'] = df['transaction_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
df['last_login_date'] = df['last_login_date'].dt.strftime('%Y-%m-%d %H:%M:%S')

df.to_csv(output_file, index=False)
print(f"generated {num_records} records. saved to '{output_file}'.")