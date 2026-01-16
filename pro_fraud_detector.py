import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os

# --- конфигурация ---
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] - %(message)s')
data_file = 'transactions.csv'

# --- генератор данных (если файла нет) ---
def generate_synthetic_data(num_users=10, num_transactions=1000):
    logging.info("генерация синтетических данных...")
    users = [f'user_{i}' for i in range(num_users)]
    ips = [f'192.168.1.{i}' for i in range(5)]
    risky_ips = [f'91.200.12.{i}' for i in range(5)]  # "иностранные" ip
    all_ips = ips + risky_ips

    data = []
    # создаем словари для отслеживания последнего состояния каждого юзера
    last_transaction_time = {user: datetime.now() - timedelta(days=365) for user in users}
    last_ip = {user: np.random.choice(ips) for user in users}

    for _ in range(num_transactions):
        user = np.random.choice(users)
        
        # симулируем течение времени
        time_since_last = timedelta(hours=np.random.uniform(1, 200))
        timestamp = last_transaction_time[user] + time_since_last
        
        # обычная транзакция
        amount = np.random.lognormal(3, 1) * 10
        category = np.random.choice(['groceries', 'transport', 'bills', 'entertainment'])
        ip = last_ip[user]

        # --- внедряем аномалии для детектора ---
        roll = np.random.rand()
        if roll > 0.98:  # спящий аккаунт проснулся
            timestamp = last_transaction_time[user] + timedelta(days=np.random.randint(100, 200))
            amount *= 5
            logging.info(f"внедряем аномалию: активность спящего аккаунта для {user}")
        elif roll > 0.95:  # смена ip + крупный перевод
            ip = np.random.choice(risky_ips)
            amount = np.random.lognormal(5, 1) * 20
            category = 'wire_transfer'
            logging.info(f"внедряем аномалию: смена ip для {user}")
        elif roll > 0.92:  # рискованная категория
            category = np.random.choice(['gambling', 'crypto_exchange'])
            amount *= 3
            logging.info(f"внедряем аномалию: рискованная категория для {user}")

        data.append([user, timestamp, amount, category, ip])
        last_transaction_time[user] = timestamp
        last_ip[user] = ip

    df = pd.DataFrame(data, columns=['user_id', 'timestamp', 'amount', 'category', 'ip_address'])
    df = df.sort_values(by='timestamp').reset_index(drop=True)
    df.to_csv(data_file, index=False)
    logging.info(f"сгенерировано и сохранено {len(df)} транзакций в {data_file}")
    return df

def load_data():
    if os.path.exists(data_file):
        logging.info(f"загрузка данных из {data_file}")
        df = pd.read_csv(data_file, parse_dates=['timestamp'])
        return df
    else:
        logging.warning(f"{data_file} не найден.")
        return generate_synthetic_data()

# --- движок анализа ---
def analyze_transactions(df):
    logging.info("запуск профессионального анализа...")
    df = df.sort_values(by=['user_id', 'timestamp'])
    
    # вычисляем разницу во времени и ip для каждого юзера
    df['time_since_last_tx'] = df.groupby('user_id')['timestamp'].diff().dt.total_seconds() / 3600  # в часах
    df['last_ip'] = df.groupby('user_id')['ip_address'].shift(1)
    df['ip_changed'] = (df['ip_address'] != df['last_ip']) & df['last_ip'].notna()

    # --- правила детекции ---
    risky_categories = ['gambling', 'crypto_exchange', 'wire_transfer']
    dormant_threshold_days = 90  # 3 месяца
    high_value_threshold = 5000

    print("\n" + "="*80)
    print(" " * 25 + "ЛОГ ПРОФЕССИОНАЛЬНОГО АНТИФРОДА")
    print("="*80 + "\n")

    alert_count = 0
    for index, row in df.iterrows():
        alerts = []
        
        # правило 1: активность спящего аккаунта
        if pd.notna(row['time_since_last_tx']) and (row['time_since_last_tx'] / 24 > dormant_threshold_days):
            alerts.append(f"СПЯЩИЙ АККАУНТ: пользователь {row['user_id']} активен после {int(row['time_since_last_tx']/24)} дней простоя.")

        # правило 2: смена ip + крупная сумма
        if row['ip_changed'] and row['amount'] > high_value_threshold:
            alerts.append(f"СМЕНА IP: пользователь {row['user_id']} совершил крупный перевод (${row['amount']:.2f}) с нового ip {row['ip_address']}.")

        # правило 3: рискованная категория
        if row['category'] in risky_categories:
            alerts.append(f"РИСКОВАННАЯ КАТЕГОРИЯ: перевод (${row['amount']:.2f}) от {row['user_id']} в категорию '{row['category']}'.")

        # правило 4: просто очень крупная сумма (менее критично, если нет других алертов)
        if not alerts and row['amount'] > high_value_threshold * 1.5:
             alerts.append(f"КРУПНАЯ СУММА: пользователь {row['user_id']} совершил необычно крупный перевод на ${row['amount']:.2f}.")

        if alerts:
            alert_count += 1
            logging.warning(f"обнаружена подозрительная активность для {row['user_id']} в {row['timestamp']}")
            print(f"[ALERT] {row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} | {alerts[0]}")
            if len(alerts) > 1:
                for extra_alert in alerts[1:]:
                    print(f"        [EXTRA] {extra_alert}")
            print(f"        [ACTION] рекомендуется ручная проверка. id транзакции: {index}\n")
    
    print("="*80)
    if alert_count == 0:
        print(" " * 25 + "подозрительных транзакций не найдено")
    else:
        print(f" " * 28 + f"АНАЛИЗ ЗАВЕРШЕН. найдено {alert_count} алертов.")
    print("="*80 + "\n")


# --- точка входа ---
if __name__ == "__main__":
    transactions_df = load_data()
    analyze_transactions(transactions_df)
