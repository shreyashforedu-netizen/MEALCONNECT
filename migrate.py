import sqlite3
import os
import shutil

DB_PATH = 'mealconnect.db'

def migrate_db():
    print("Starting database migration...")
    
    # Backup database
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, 'mealconnect_backup.db')
        print("Backup created at mealconnect_backup.db")
        
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. Hotels: add status, lat, lon, guest_count
    try:
        cur.execute("ALTER TABLE hotels ADD COLUMN status TEXT DEFAULT 'Approved'")
        cur.execute("ALTER TABLE hotels ADD COLUMN lat REAL")
        cur.execute("ALTER TABLE hotels ADD COLUMN lon REAL")
        cur.execute("ALTER TABLE hotels ADD COLUMN guest_count INTEGER DEFAULT 100")
        print("Updated hotels table.")
    except sqlite3.OperationalError as e:
        print(f"Hotels update skipped (might already exist): {e}")

    # 2. NGOs: migrate from INTEGER id to TEXT id, add password_hash, status, lat, lon
    try:
        # We need to recreate the NGOs table if we are changing the primary key type.
        # But wait, SQLite allows storing TEXT in INTEGER PK if not STRICT, but it's safer to recreate.
        cur.execute("CREATE TABLE IF NOT EXISTS ngos_new (id TEXT PRIMARY KEY, name TEXT NOT NULL, contact_person TEXT, phone TEXT, email TEXT UNIQUE, location TEXT, password_hash TEXT, status TEXT DEFAULT 'Approved', lat REAL, lon REAL)")
        
        # Check if old table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ngos'")
        if cur.fetchone():
            cur.execute("SELECT * FROM ngos")
            old_ngos = cur.fetchall()
            for row in old_ngos:
                # row is (id, name, contact_person, phone, email, location)
                old_id = str(row[0])
                new_id = f"N{old_id.zfill(3)}" if old_id.isdigit() else old_id
                cur.execute("INSERT INTO ngos_new (id, name, contact_person, phone, email, location) VALUES (?, ?, ?, ?, ?, ?)", (new_id, row[1], row[2], row[3], row[4], row[5]))
            
            cur.execute("DROP TABLE ngos")
            
        cur.execute("ALTER TABLE ngos_new RENAME TO ngos")
        print("Migrated ngos table.")
    except sqlite3.OperationalError as e:
        print(f"NGOs migration skipped or error: {e}")

    # 3. Admins table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # 4. Alerts table: expand columns
    try:
        cur.execute("ALTER TABLE alerts ADD COLUMN accepted_by_ngo_id TEXT")
        cur.execute("ALTER TABLE alerts ADD COLUMN pickup_slot_start TEXT")
        cur.execute("ALTER TABLE alerts ADD COLUMN pickup_slot_end TEXT")
        print("Updated alerts table.")
    except sqlite3.OperationalError as e:
        print(f"Alerts update skipped (might already exist): {e}")
        
    # 5. FoodItems (Dishes) table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id TEXT NOT NULL,
            entry_date DATE NOT NULL,
            dish_name TEXT NOT NULL,
            category TEXT,
            dietary_type TEXT, -- Veg/Non-Veg
            prepared_kg REAL NOT NULL,
            consumed_kg REAL NOT NULL,
            waste_kg REAL NOT NULL,
            FOREIGN KEY(hotel_id) REFERENCES hotels(id)
        )
    ''')
    
    # 6. Notifications table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_type TEXT NOT NULL, -- 'hotel', 'ngo', 'admin'
            user_id TEXT NOT NULL,
            message TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 7. Reviews table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_type TEXT NOT NULL,
            from_id TEXT NOT NULL,
            to_type TEXT NOT NULL,
            to_id TEXT NOT NULL,
            alert_id INTEGER,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(alert_id) REFERENCES alerts(id)
        )
    ''')
    
    # Update foreign keys in collections to handle TEXT ngo_id if needed. SQLite does weak typing so it should be fine.
    
    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate_db()
