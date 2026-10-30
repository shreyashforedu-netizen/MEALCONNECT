import os

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('@login_required', '@role_required(\'hotel\')')
content = content.replace("hotel_id = session.get('hotel_id')", "hotel_id = session.get('user_id')")
content = content.replace("hotel_id = session['hotel_id']", "hotel_id = session['user_id']")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
