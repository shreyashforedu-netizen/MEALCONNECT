with open('static/css/home.css', 'r', encoding='utf-8') as f:
    css = f.read()

light_vars = '''
:root[data-theme="light"] {
  --bg-color: #f8fafc;
  --surface-color: #ffffff;
  --surface-border: rgba(0, 0, 0, 0.1);
  --text-main: #0f172a;
  --text-muted: #64748b;
  --secondary: rgba(0, 0, 0, 0.05);
  --secondary-hover: rgba(0, 0, 0, 0.1);
}
'''
if 'data-theme="light"' not in css:
    css = css + light_vars
    with open('static/css/home.css', 'w', encoding='utf-8') as f:
        f.write(css)
    print('Added light theme to home.css')
