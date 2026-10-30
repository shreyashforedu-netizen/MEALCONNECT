import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import datetime

def get_hotel_data(hotel_id, db_path):
    conn = sqlite3.connect(db_path)
    query = "SELECT entry_date, prepared_kg, consumed_kg, waste_kg FROM food_entries WHERE hotel_id = ? ORDER BY entry_date ASC"
    df = pd.read_sql_query(query, conn, params=(hotel_id,))
    conn.close()
    return df

def create_features(df):
    df['entry_date'] = pd.to_datetime(df['entry_date'])
    # Target is the next day's waste. So we shift waste_kg backwards by 1.
    df['target_waste'] = df['waste_kg'].shift(-1)
    
    # We also need the target's day of week
    df['target_day_of_week'] = df['entry_date'].dt.dayofweek.shift(-1)
    
    # Existing features (current day)
    df['prev_prepared'] = df['prepared_kg']
    df['prev_consumed'] = df['consumed_kg']
    df['prev_waste'] = df['waste_kg']
    
    # Rolling average of waste
    df['rolling_3d_waste'] = df['waste_kg'].rolling(window=3, min_periods=1).mean()
    
    return df

def predict_tomorrow_waste(hotel_id, db_path):
    df = get_hotel_data(hotel_id, db_path)
    
    # Check if there is enough data
    if len(df) < 5:
        # Fallback to simple average
        if len(df) == 0:
            return 0.0, True
        return round(float(df['waste_kg'].mean()), 2), True
        
    df = create_features(df)
    
    # To train, we drop the last row because it has no 'target_waste'
    train_df = df.dropna(subset=['target_waste']).copy()
    
    features = ['target_day_of_week', 'prev_prepared', 'prev_consumed', 'prev_waste', 'rolling_3d_waste']
    
    X = train_df[features]
    y = train_df['target_waste']
    
    # Need at least a few samples for train_test_split
    if len(train_df) < 3:
        # Not enough to split
        return round(float(df['waste_kg'].mean()), 2), True
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    rf = RandomForestRegressor(n_estimators=50, random_state=42)
    lr = LinearRegression()
    
    rf.fit(X_train, y_train)
    lr.fit(X_train, y_train)
    
    rf_mse = mean_squared_error(y_test, rf.predict(X_test))
    lr_mse = mean_squared_error(y_test, lr.predict(X_test))
    
    best_model = rf if rf_mse < lr_mse else lr
    
    # Now predict tomorrow based on the LAST row of df
    last_row = df.iloc[-1]
    tomorrow = last_row['entry_date'] + datetime.timedelta(days=1)
    
    X_pred = pd.DataFrame([{
        'target_day_of_week': tomorrow.dayofweek,
        'prev_prepared': last_row['prev_prepared'],
        'prev_consumed': last_row['prev_consumed'],
        'prev_waste': last_row['prev_waste'],
        'rolling_3d_waste': last_row['rolling_3d_waste']
    }])
    
    pred = best_model.predict(X_pred)[0]
    
    # Prevent negative predictions
    final_pred = max(0.0, float(pred))
    return round(final_pred, 2), False
