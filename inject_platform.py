import os
import glob
import re

head_script = '''
  <script src="{{ url_for('static', filename='js/theme.js') }}"></script>
'''

buttons_html = '''
        <!-- Platform Features -->
        <button id="theme-toggle" class="btn btn-outline btn-sm" style="border:none; font-size:1.2rem; padding:0.5rem;" title="Toggle Theme">
          <i id="theme-toggle-icon" class="ri-moon-line"></i>
        </button>
        <div style="position:relative;">
          <a href="{{ url_for('notifications') }}" class="btn btn-outline btn-sm" style="border:none; font-size:1.2rem; padding:0.5rem;" title="Notifications">
            <i class="ri-notification-3-line"></i>
            {% if unread_notifications %}
            <span style="position:absolute; top:0px; right:0px; background:#e74c3c; width:10px; height:10px; border-radius:50%;"></span>
            {% endif %}
          </a>
        </div>
'''

nav_profile_html = '''
      <a href="{{ url_for('profile') }}" class="nav-item {% if request.endpoint == 'profile' %}active{% endif %}">
        <i class="ri-settings-4-line"></i> Settings
      </a>
'''

for filepath in glob.glob('templates/*.html'):
    if 'intro.html' in filepath or 'login.html' in filepath or 'signup.html' in filepath:
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    # 1. Add theme.js to head
    if 'js/theme.js' not in content:
        content = content.replace('</head>', f'{head_script}</head>')
        modified = True
        
    # 2. Add buttons to top-bar. They usually have a div with display:flex or just directly inside top-bar
    if 'theme-toggle' not in content:
        # Find the div inside top-bar that contains the buttons
        pattern = re.compile(r'(<div class="top-bar">.*?)<div style="display: flex; gap: 1rem.*?">', re.DOTALL)
        if pattern.search(content):
            content = re.sub(r'(<div style="display: flex; gap: 1rem.*?">)', r'\1\n' + buttons_html, content)
            modified = True
            
    # 3. Add Settings to nav-menu before logout
    if 'url_for(\'profile\')' not in content:
        content = content.replace('<a href="{{ url_for(\'logout\') }}"', nav_profile_html + '\n      <a href="{{ url_for(\'logout\') }}"')
        modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
