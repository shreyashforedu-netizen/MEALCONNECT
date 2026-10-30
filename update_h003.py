import sqlite3
conn = sqlite3.connect('mealconnect.db')
cur = conn.cursor()
cur.execute("UPDATE hotels SET lat = 19.0330, lon = 73.0166, address = 'Nerul, Navi Mumbai' WHERE id = 'H003'")
conn.commit()
print("Updated H003 successfully")
