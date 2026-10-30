import sqlite3
import datetime
import random
from werkzeug.security import generate_password_hash

DB_PATH = 'mealconnect.db'

def reset_and_seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Clearing database...")
    tables = ['collections', 'alerts', 'predictions', 'food_entries', 'ngos', 'hotels']
    for table in tables:
        cur.execute(f"DELETE FROM {table}")
        
    print("Seeding Hotels...")
    hotels = [
        ('H001', 'Grand Plaza Hotel', 'John Smith', 'grand@example.com', '1234567890', 'Hotel', '123 Grand Ave', generate_password_hash('password123'), 25.0),
        ('H002', 'City Bistro', 'Jane Doe', 'city@example.com', '0987654321', 'Restaurant', '456 City St', generate_password_hash('password123'), 15.0)
    ]
    cur.executemany("INSERT INTO hotels (id, hotel_name, owner_name, email, phone, hotel_type, address, password_hash, threshold_kg) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", hotels)

    print("Seeding NGOs...")
    ngos = [
        ('Helping Hands', 'Alice', '1111111111', 'alice@helping.org', 'Downtown'),
        ('Food Bank City', 'Bob', '2222222222', 'bob@foodbank.org', 'Uptown'),
        ('Care & Share', 'Charlie', '3333333333', 'charlie@care.org', 'Midtown'),
        ('Zero Waste NGO', 'Diana', '4444444444', 'diana@zerowaste.org', 'Suburbs'),
        ('Community Kitchen', 'Eve', '5555555555', 'eve@community.org', 'Westside')
    ]
    for ngo in ngos:
        cur.execute("INSERT INTO ngos (name, contact_person, phone, email, location) VALUES (?, ?, ?, ?, ?)", ngo)
    
    # Get inserted NGO IDs
    cur.execute("SELECT id FROM ngos")
    ngo_ids = [row[0] for row in cur.fetchall()]

    print("Seeding 30 days of data for hotels...")
    today = datetime.date.today()
    
    for hotel_id, _, _, _, _, _, _, _, threshold in hotels:
        for i in range(30, 0, -1):
            current_date = today - datetime.timedelta(days=i)
            date_str = current_date.isoformat()
            
            # Food Entry
            prepared = random.uniform(100, 200)
            consumed = prepared * random.uniform(0.7, 0.95)
            waste = prepared - consumed
            
            cur.execute("INSERT INTO food_entries (hotel_id, entry_date, prepared_kg, consumed_kg, waste_kg, notes) VALUES (?, ?, ?, ?, ?, ?)",
                        (hotel_id, date_str, round(prepared, 2), round(consumed, 2), round(waste, 2), "Seeded entry"))
            
            # Predict previous day for this date (simulated)
            # In a real system, the prediction for 'today' was made yesterday.
            predicted_waste = waste * random.uniform(0.8, 1.2) # +/- 20% error
            is_high = predicted_waste > threshold
            
            cur.execute("INSERT INTO predictions (hotel_id, for_date, predicted_waste, threshold, exceeded_flag) VALUES (?, ?, ?, ?, ?)",
                        (hotel_id, date_str, round(predicted_waste, 2), threshold, 1 if is_high else 0))
            prediction_id = cur.lastrowid
            
            # If high waste, maybe create an alert and collection
            if is_high and random.choice([True, False, True]): # 66% chance to create alert if high
                reserved = predicted_waste * random.uniform(0.9, 1.0)
                ngo_id = random.choice(ngo_ids)
                
                # 80% chance it was completed
                status = 'Completed' if random.random() < 0.8 else 'Pending'
                
                cur.execute("INSERT INTO alerts (hotel_id, ngo_id, prediction_id, expected_date, predicted_waste, reserved_kg, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (hotel_id, ngo_id, prediction_id, date_str, round(predicted_waste, 2), round(reserved, 2), status))
                alert_id = cur.lastrowid
                
                if status == 'Completed':
                    collected = reserved * random.uniform(0.8, 1.0)
                    cur.execute('''
                        INSERT INTO collections (alert_id, hotel_id, ngo_id, collection_date, predicted_waste, actual_waste, reserved_kg, collected_kg, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Completed')
                    ''', (alert_id, hotel_id, ngo_id, date_str, round(predicted_waste, 2), round(waste, 2), round(reserved, 2), round(collected, 2)))

    conn.commit()
    conn.close()
    print("Seed complete! You can log in with grand@example.com / password123")

if __name__ == '__main__':
    reset_and_seed()
