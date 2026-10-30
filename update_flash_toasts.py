import os
import glob
import re

toast_html = '''
    <!-- Toast Messages -->
    <div class="toast-container" id="toast-container">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="toast {{ category }}">
            <span>{{ message }}</span>
            <button onclick="this.parentElement.remove()" style="background:none; border:none; color:inherit; cursor:pointer; margin-left:auto;"><i class="ri-close-line"></i></button>
          </div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    </div>
    <script>
      setTimeout(() => {
        const toasts = document.querySelectorAll('.toast');
        toasts.forEach(toast => {
          toast.style.animation = 'fadeOut 0.3s forwards cubic-bezier(0.25, 0.8, 0.25, 1)';
          setTimeout(() => toast.remove(), 300);
        });
      }, 5000);
    </script>
'''

pattern = re.compile(r"<!-- Flash Messages -->\s*{% with messages = get_flashed_messages.*?{% endwith %}", re.DOTALL)

for filepath in glob.glob('templates/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "<!-- Flash Messages -->" in content:
        new_content = pattern.sub(toast_html.strip(), content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
