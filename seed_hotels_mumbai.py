import sqlite3
import random

def seed_hotels():
    conn = sqlite3.connect('mealconnect.db')
    cur = conn.cursor()
    
    # 1. Define Mumbai/Navi Mumbai hypothetical hotels
    hotels_data = [
        ("Mumbai Grand", "Mumbai Region", 19.0760, 72.8777, "Luxury Hotel"),
        ("Sea View Resort", "Mumbai Region", 19.0550, 72.8300, "Resort"),
        ("The Gateway Inn", "Mumbai Region", 18.9220, 72.8347, "Boutique Hotel"),
        ("Navi Mumbai Suites", "Navi Mumbai", 19.0330, 73.0297, "Business Hotel"),
        ("Vashi Plaza Hotel", "Navi Mumbai", 19.0745, 72.9978, "Luxury Hotel"),
        ("Powai Lakeside", "Mumbai Region", 19.1176, 72.9060, "Boutique Hotel"),
        ("Andheri Business Lodge", "Mumbai Region", 19.1136, 72.8697, "Business Hotel"),
        ("Thane Central Hotel", "Thane", 19.2183, 72.9781, "Resort"),
        ("Kharghar Hills Resort", "Navi Mumbai", 19.0368, 73.0682, "Resort"),
        ("Bandra Kurla Suites", "Mumbai Region", 19.0653, 72.8658, "Business Hotel")
    ]
    
    # Get current hotel count to start IDs properly
    cur.execute("SELECT COUNT(*) FROM hotels")
    count = cur.fetchone()[0]
    
    for i, data in enumerate(hotels_data):
        h_id = f"HMUM{i+1:03d}"
        name, address, lat, lon, h_type = data
        
        # Check if exists
        cur.execute("SELECT * FROM hotels WHERE id=?", (h_id,))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO hotels (id, hotel_name, owner_name, email, phone, hotel_type, address, password_hash, lat, lon, threshold_kg)
                VALUES (?, ?, 'Admin', ?, '9999999999', ?, ?, 'dummy_hash', ?, ?, 20.0)
            """, (h_id, name, f"admin_{h_id}@hotel.com", h_type, address, lat, lon))
            
    conn.commit()
    print("Added 10 hypothetical hotels in Mumbai/Navi Mumbai.")

if __name__ == '__main__':
    seed_hotels()
