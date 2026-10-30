import os
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

ctx_processor = '''
@app.context_processor
def inject_global_vars():
    unread = 0
    if 'hotel_id' in session:
        try:
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0", (session['hotel_id'],))
                row = cur.fetchone()
                if row:
                    unread = row[0]
        except:
            pass
    return dict(unread_notifications=unread)
'''

pattern = re.compile(r'# Routes\n@app\.route')
content = pattern.sub(ctx_processor + '\n# Routes\n@app.route', content)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
