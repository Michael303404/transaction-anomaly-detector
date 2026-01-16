import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta
import os

# генерируем фейковые транзакции, чтобы было на чем тренироваться
def generate_sample_data(n_transactions=1000):
    np.random.seed(42)  # для воспроизводимости
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=np.random.randint(0, 365)) for _ in range(n_transactions)]
    categories = np.random.choice(['groceries', 'transport', 'entertainment', 'salary', 'bills'], n_transactions)
    amounts = np.random.normal(50, 30, n_transactions)
    amounts = np.clip(amounts, 0, None)  # убираем отрицательные суммы

    # специально вбрасываем аномалии: несколько очень крупных трат
    anomaly_indices = np.random.choice(n_transactions, size=20, replace=False)
    amounts[anomaly_indices] = np.random.uniform(500, 2000, 20)
    
    df = pd.DataFrame({
        'timestamp': pd.to_datetime(dates),
        'category': categories,
        'amount': amounts
    })
    df = df.sort_values('timestamp').reset_index(drop=True)
    return df

# основная функция детекции
def detect_anomalies(df):
    # фичи для модели: сумма, час дня и категория (закодированная в цифры)
    df['hour'] = df['timestamp'].dt.hour
    df_encoded = pd.get_dummies(df[['amount', 'hour', 'category']], drop_first=True)
    
    # IsolationForest - отлично подходит для поиска "белых ворон"
    model = IsolationForest(contamination=0.05, random_state=42)  # предполагаем, что 5% транзакций - аномалии
    model.fit(df_encoded)
    df['anomaly'] = model.predict(df_encoded)
    df['anomaly'] = df['anomaly'].map({1: 0, -1: 1})  # переводим в удобный формат: 1 - аномалия, 0 - норма
    
    return df

# точка входа
if __name__ == "__main__":
    df = generate_sample_data()
    df_with_anoms = detect_anomalies(df)
    
    # выводим статистику
    total_anoms = df_with_anoms['anomaly'].sum()
    print(f"обработано {len(df)} транзакций. найдено {total_anoms} аномалий.")
    print("\nпоследние 5 аномалий:")
    print(df_with_anoms[df_with_anoms['anomaly'] == 1][['timestamp', 'category', 'amount']].tail(5))
    
    # сохраняем полный отчет в csv файл
    output_file = 'anomaly_report.csv'