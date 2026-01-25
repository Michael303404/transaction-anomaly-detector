import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta
import os

# generate fake transactions for testing
def generate_sample_data(n_transactions=1000):
    np.random.seed(42)  # for reproducibility
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=np.random.randint(0, 365)) for _ in range(n_transactions)]
    categories = np.random.choice(['groceries', 'transport', 'entertainment', 'salary', 'bills'], n_transactions)
    amounts = np.random.normal(50, 30, n_transactions)
    amounts = np.clip(amounts, 0, None)  # remove negative amounts

    # deliberately inject anomalies: several very large transactions
    anomaly_indices = np.random.choice(n_transactions, size=20, replace=False)
    amounts[anomaly_indices] = np.random.uniform(500, 2000, 20)
    
    df = pd.DataFrame({
        'timestamp': pd.to_datetime(dates),
        'category': categories,
        'amount': amounts
    })
    df = df.sort_values('timestamp').reset_index(drop=True)
    return df

# main detection function
def detect_anomalies(df):
    # features for the model: amount, hour of day, and category (encoded as numbers)
    df['hour'] = df['timestamp'].dt.hour
    df_encoded = pd.get_dummies(df[['amount', 'hour', 'category']], drop_first=True)
    
    # IsolationForest - perfect for finding outliers
    model = IsolationForest(contamination=0.05, random_state=42)  # assume 5% of transactions are anomalies
    model.fit(df_encoded)
    df['anomaly'] = model.predict(df_encoded)
    df['anomaly'] = df['anomaly'].map({1: 0, -1: 1})  # convert to readable format: 1 - anomaly, 0 - normal
    
    return df

# entry point
if __name__ == "__main__":
    df = generate_sample_data()
    df_with_anoms = detect_anomalies(df)
    
    # output statistics
    total_anoms = df_with_anoms['anomaly'].sum()
    print(f"processed {len(df)} transactions. found {total_anoms} anomalies.")
    print("\nlast 5 anomalies:")
    print(df_with_anoms[df_with_anoms['anomaly'] == 1][['timestamp', 'category', 'amount']].tail(5))
    
    # save full report to csv file
    output_file = 'anomaly_report.csv'