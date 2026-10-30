import sqlite3
import random
from werkzeug.security import generate_password_hash

def seed_mumbai():
    conn = sqlite3.connect('mealconnect.db')
    cur = conn.cursor()
    
    # 1. Update Hotel H001 to Navi Mumbai (Vashi)
    cur.execute("UPDATE hotels SET lat = 19.0770, lon = 72.9989 WHERE id = 'H001'")
    
    # 2. Random NGO names and contact people
    ngo_names = [
        "Mumbai Food Rescue", "Navi Mumbai Feeders", "Aahar Foundation", 
        "Zero Hunger Initiative", "Bandra Care Trust", "Andheri Meals", 
        "Thane Food Bank", "Dadar Charity", "Marine Drive Samaritans", 
        "Vashi Compassion", "Juhu Relief", "Colaba Hand of Hope", 
        "Panvel Provisions", "Kharghar Food Network", "Chembur Care"
    ]
    
    contacts = ["Amit", "Priya", "Rahul", "Sneha", "Vikram", "Neha", "Rohan", "Pooja", "Siddharth", "Anjali"]
    
    # 3. Generate 15 random NGOs in Mumbai/Navi Mumbai region
    # Mumbai bounding box approx: Lat 18.90 to 19.25, Lon 72.80 to 73.15
    for i in range(15):
        ngo_id = f"MUM{i+1:03d}"
        name = ngo_names[i]
        contact = random.choice(contacts)
        phone = f"98{random.randint(10000000, 99999999)}"
        email = f"contact_{i}@mumbai-ngo.org"
        location = "Mumbai Region"
        
        # Generate random coordinates
        lat = random.uniform(18.90, 19.20)
        lon = random.uniform(72.82, 73.10)
        
        try:
            cur.execute("""
                INSERT INTO ngos (id, name, contact_person, phone, email, location, password_hash, status, lat, lon)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Approved', ?, ?)
            """, (ngo_id, name, contact, phone, email, location, generate_password_hash('password123'), lat, lon))
        except sqlite3.IntegrityError:
            cur.execute("UPDATE ngos SET lat = ?, lon = ? WHERE id = ?", (lat, lon, ngo_id))
            
    conn.commit()
    conn.close()
    print("Successfully seeded 15 NGOs in Mumbai/Navi Mumbai!")

if __name__ == '__main__':
    seed_mumbai()
