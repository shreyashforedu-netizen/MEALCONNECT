import os
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'import mailer' not in content:
    content = content.replace('import sqlite3', 'import sqlite3\nimport mailer')
    
# Replace the alert creation to include notification
alert_creation = '''
            conn.execute("INSERT INTO alerts (hotel_id, ngo_id, prediction_id, expected_date, predicted_waste, reserved_kg, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (hotel_id, ngo_id if ngo_id != 'Broadcast' else None, prediction_id, expected_date, pred['predicted_waste'], reserved_kg, 'Pending'))
            conn.commit()
            
            # Send notification
            cur = conn.cursor()
            cur.execute("SELECT email, email_notifications FROM hotels WHERE id = ?", (hotel_id,))
            hotel_data = cur.fetchone()
            if hotel_data:
                mailer.create_notification(
                    conn, 
                    'hotel', 
                    hotel_id, 
                    f"Alert sent to {'broadcast' if ngo_id == 'Broadcast' else 'NGO'} for {reserved_kg}kg of food.",
                    hotel_data['email'] if hotel_data['email_notifications'] else None,
                    "Meal Connect: Alert Sent"
                )
'''
content = re.sub(r'conn\.execute\("INSERT INTO alerts.*?conn\.commit\(\)', alert_creation.strip(), content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
