import pandas as pd
import config # loads external settings (your playground)

def analyze_transactions():
    """
    analyzes transaction data for fraudulent patterns using vectorized operations.
    """
    try:
        df = pd.read_csv(config.data_file)
    except FileNotFoundError:
        print(f"error: data file not found at '{config.data_file}'.")
        return
    
    # --- vectorized analysis ---
    
    # 1. convert date columns to datetime objects once (trust me - it matters)
    df['last_login_date'] = pd.to_datetime(df['last_login_date'])
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # 2. calculate dormancy for all rows at once (no for loops here)
    df['dormancy_days'] = (df['transaction_date'] - df['last_login_date']).dt.days
    
    # 3. define boolean filters for each condition (this is the fun part)
    is_high_value = df['amount'] > config.high_value_threshold # don't forget the money!
    is_dormant = df['dormancy_days'] > config.dormant_threshold_days # dusty accounts are a red flag.
    is_risky_category = df['transaction_category'].isin(config.risky_categories)
    is_suspicious_ip = df['ip_address'].isin(config.suspicious_ip_addresses)
    
    # 4. combine filters to find all fraudulent transactions (this reads like poetry)
    # a transaction triggers an alert if it meets *any* of the conditions ( | means 'or' )
    alerts_df = df[is_high_value | is_dormant | is_risky_category | is_suspicious_ip].copy()
    
    # --- reporting ---
    print("analysis complete.")
    
    if not alerts_df.empty:
        print(f"{len(alerts_df)} alerts found.")
        # to see the actual alerts, uncomment the line below (i won't judge)
        # print(alerts_df)
        
        # persist the findings (data is useless if it vanishes)
        try:
            alerts_df.to_csv('fraud_alerts.csv', index=False)
            print("report saved to 'fraud_alerts.csv'.")
        except Exception as e:
            print(f"failed to save report to 'fraud_alerts.csv'. error:\n{e}")
            
        print("done.")
        
        # if you want to email yourself the report... that's a feature for another day.
        
    else:
        print("no suspicious activity detected.")

if __name__ == "__main__":
    analyze_transactions()