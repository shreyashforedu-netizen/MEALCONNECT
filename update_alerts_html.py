import re

with open('templates/alerts.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the select block
new_select = '''
            <select name="ngo_id" class="form-input" style="flex-grow:1;" required>
              <option value="Broadcast">Broadcast to All</option>
              <option value="Nearest" style="font-weight:bold; color:var(--primary);">Send to Nearest NGO (Auto-assign)</option>
              {% for ngo in ngos %}
                <option value="{{ ngo.id }}">{{ ngo.name }} ({{ ngo.dist }} km away)</option>
              {% endfor %}
            </select>
'''

content = re.sub(r'<select name="ngo_id".*?</select>', new_select.strip(), content, flags=re.DOTALL)

with open('templates/alerts.html', 'w', encoding='utf-8') as f:
    f.write(content)
