import os

for filename in ['templates/map.html', 'templates/ngo_dashboard.html']:
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        css_addition = '''
      .main-content { flex-grow: 1; padding: 2rem 3rem; overflow-y: auto; position: relative; }
      .panel { padding: 1.5rem; border-radius: 16px; margin-bottom: 2rem; }
      .panel-title { font-size: 1.2rem; font-family: var(--font-display); margin-bottom: 1.5rem; }
'''
        
        if '.main-content {' not in content:
            content = content.replace('</style>', css_addition + '</style>')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
