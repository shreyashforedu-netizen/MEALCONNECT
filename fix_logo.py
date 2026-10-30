import os, glob

for filepath in glob.glob('templates/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    target = '<div class="sidebar-logo nav-logo">\n      <i class="ri-leaf-line"></i> Meal Connect\n    </div>'
    replacement = '<a href="{{ url_for(\'index\') }}" class="sidebar-logo nav-logo" style="text-decoration:none; color:inherit; display:flex; align-items:center; cursor:pointer;">\n      <i class="ri-leaf-line" style="margin-right: 8px;"></i> Meal Connect\n    </a>'
    
    if target in content:
        content = content.replace(target, replacement)
    else:
        # Fallback if there are minor spacing differences
        import re
        content = re.sub(r'<div class="sidebar-logo nav-logo">\s*<i class="ri-leaf-line"></i> Meal Connect\s*</div>', replacement, content)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
