import os, glob

for filepath in glob.glob('templates/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace '#' with correct url_for
    content = content.replace('<a href="#" class="nav-item"><i class="ri-brain-line"></i> Prediction</a>', '<a href="{{ url_for(\'prediction\') }}" class="nav-item"><i class="ri-brain-line"></i> Prediction</a>')
    content = content.replace('<a href="#" class="nav-item"><i class="ri-notification-3-line"></i> Alerts</a>', '<a href="{{ url_for(\'alerts\') }}" class="nav-item"><i class="ri-notification-3-line"></i> Alerts</a>')
    content = content.replace('<a href="#" class="nav-item"><i class="ri-history-line"></i> Collection History</a>', '<a href="{{ url_for(\'history\') }}" class="nav-item"><i class="ri-history-line"></i> Collection History</a>')
    content = content.replace('<a href="#" class="nav-item"><i class="ri-bar-chart-box-line"></i> Business Analytics</a>', '<a href="{{ url_for(\'analytics\') }}" class="nav-item"><i class="ri-bar-chart-box-line"></i> Business Analytics</a>')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
