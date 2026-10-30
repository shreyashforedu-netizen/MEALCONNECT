import os

def inject_export(filepath, export_type):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    buttons = f'''
        <div style="display:flex; gap:0.5rem;">
          <a href="{{{{ url_for('export_data', format='csv', type='{export_type}') }}}}" class="btn btn-outline btn-sm"><i class="ri-file-excel-line"></i> CSV</a>
          <a href="{{{{ url_for('export_data', format='pdf', type='{export_type}') }}}}" class="btn btn-outline btn-sm"><i class="ri-file-pdf-line"></i> PDF</a>
        </div>
    '''
    
    # We need to find the panel header and put it there. 
    # Example in history: <h2 class="panel-title">Recent Collections</h2>
    import re
    # We'll replace the closing h2 with closing h2 + buttons, wrapped in a flex container if not already.
    # Actually, simpler to just find `<h2 class="panel-title">...</h2>` and if we don't have the buttons yet, inject them.
    if "ri-file-excel-line" not in content:
        pattern = re.compile(r'(<h2 class="panel-title">.*?</h2>)')
        # Replace the first occurrence of panel-title
        match = pattern.search(content)
        if match:
            # We want to wrap it so it justifies space-between if it isn't already.
            # But the parent might already be flex. Let's just insert it after the h2.
            # Actually, most headers are inside `<div class="panel-header">` which we can make flex space-between.
            content = content.replace('<div class="panel-header">', '<div class="panel-header" style="display:flex; justify-content:space-between; align-items:center;">', 1)
            content = content.replace(match.group(1), match.group(1) + buttons, 1)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

inject_export('templates/history.html', 'collections')
inject_export('templates/prediction.html', 'predictions')
# For food_entry.html, it's slightly different as it has a form, but let's see. Let's just inject in history and prediction for now, and maybe analytics.
