import os
import re

TEMPLATES_DIR = 'templates'
HOTEL_TEMPLATES = [
    'dashboard.html', 'food_entry.html', 'prediction.html', 
    'alerts.html', 'map.html', 'history.html', 'analytics.html', 
    'profile.html', 'notifications.html'
]

# 1. Update sidebars
badge_link = '''      <a href="{{ url_for('analytics') }}" class="nav-item"><i class="ri-bar-chart-box-line"></i> Business Analytics</a>
      <a href="{{ url_for('badge') }}" class="nav-item {% if request.endpoint == 'badge' %}active{% endif %}"><i class="ri-award-line"></i> Badge of Appreciation</a>'''

for tmpl in HOTEL_TEMPLATES:
    path = os.path.join(TEMPLATES_DIR, tmpl)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'Badge of Appreciation' not in content:
            # Replace the analytics link with analytics + badge
            search_str = '<a href="{{ url_for(\'analytics\') }}" class="nav-item"><i class="ri-bar-chart-box-line"></i> Business Analytics</a>'
            
            # Since some files might have slightly different spacing, we can use regex
            content = re.sub(
                r'<a href="\{\{ url_for\(\'analytics\'\) \}\}" class="nav-item(\s*\{%.*?%\})?"><i class="ri-bar-chart-box-line"></i> Business Analytics</a>',
                badge_link,
                content
            )
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        print(f"Updated {tmpl}")

# 2. Add route to app.py
app_py_path = 'app.py'
with open(app_py_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

route_code = """
@app.route('/badge')
@login_required
def badge():
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT hotel_name FROM hotels WHERE id = ?", (session['hotel_id'],))
            hotel = cur.fetchone()
            hotel_name = hotel['hotel_name'] if hotel else "Partner"
    except:
        hotel_name = "Partner"
    return render_template('badge.html', hotel_name=hotel_name)
"""

if "def badge():" not in app_content:
    # Insert after def analytics():
    insert_pos = app_content.find("def analytics():")
    if insert_pos != -1:
        end_of_func = app_content.find("@app.route", insert_pos)
        if end_of_func == -1:
            app_content += route_code
        else:
            app_content = app_content[:end_of_func] + route_code + "\n" + app_content[end_of_func:]
        
        with open(app_py_path, 'w', encoding='utf-8') as f:
            f.write(app_content)
        print("Added badge route to app.py")
