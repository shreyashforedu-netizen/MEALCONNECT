import sqlite3
from werkzeug.security import generate_password_hash

def seed_map_data():
    conn = sqlite3.connect('mealconnect.db')
    cur = conn.cursor()
    
    # Update Hotel H001 with dummy coordinates (Central Delhi)
    cur.execute("UPDATE hotels SET lat = 28.6139, lon = 77.2090 WHERE id = 'H001'")
    
    # Seed 3 dummy NGOs nearby
    dummy_ngos = [
        ('N001', 'SaveFood India', 'Amit Kumar', '9876543210', 'savefood@example.com', 'Connaught Place', 28.6200, 77.2100),
        ('N002', 'Feeding Hands NGO', 'Priya Singh', '9876543211', 'feeding@example.com', 'India Gate', 28.6000, 77.2200),
        ('N003', 'Hope Foundation', 'Rahul Verma', '9876543212', 'hope@example.com', 'Karol Bagh', 28.6300, 77.1900)
    ]
    
    for ngo in dummy_ngos:
        try:
            cur.execute("""
                INSERT INTO ngos (id, name, contact_person, phone, email, location, password_hash, status, lat, lon)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Approved', ?, ?)
            """, (ngo[0], ngo[1], ngo[2], ngo[3], ngo[4], ngo[5], generate_password_hash('password123'), ngo[6], ngo[7]))
        except sqlite3.IntegrityError:
            # If they already exist, just update their coordinates
            cur.execute("UPDATE ngos SET lat = ?, lon = ? WHERE email = ?", (ngo[6], ngo[7], ngo[4]))
            
    conn.commit()
    conn.close()
    print("Map data seeded successfully!")

if __name__ == '__main__':
    seed_map_data()
