import os
import glob
import re

link_to_add = '      <a href="{{ url_for(\'live_map\') }}" class="nav-item {% if request.endpoint == \'live_map\' %}active{% endif %}"><i class="ri-map-pin-line"></i> Live Map</a>'
# I'll just use the regular class="nav-item" since the active state is handled explicitly in most templates, or we can just drop it in.

target_files = [
    'dashboard.html', 'food_entry.html', 'prediction.html', 
    'alerts.html', 'history.html', 'analytics.html', 
    'profile.html', 'notifications.html'
]

for filename in target_files:
    filepath = f"templates/{filename}"
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'url_for(\'live_map\')' not in content:
            # Insert after the alerts link
            pattern = re.compile(r'(<a href="{{ url_for\(\'alerts\'\) }}".*?</a>)')
            
            # Since active states might use logic, let's just use nav-item
            nav_item_class = 'nav-item'
            if filename == 'map.html': nav_item_class = 'nav-item active'
                
            insertion = f'\n      <a href="{{{{ url_for(\'live_map\') }}}}" class="{nav_item_class}"><i class="ri-map-pin-line"></i> Live Map</a>'
            
            content = pattern.sub(r'\1' + insertion, content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
print("Injected Map link into sidebars")
