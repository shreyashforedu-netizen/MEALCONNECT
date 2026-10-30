import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

def replace_alerts_func(content):
    # We will search for def alerts(): and replace its body up to return render_template('alerts.html'
    pattern = re.compile(r"def alerts\(\):(.*?)(return render_template\('alerts\.html',.*?\))", re.DOTALL)
    match = pattern.search(content)
    if not match: return content
    
    body = match.group(1)
    ret_stmt = match.group(2)
    
    # We need to inject the NGO fetching logic that calculates distance.
    # Currently it just does: cur.execute("SELECT id, name FROM ngos WHERE status = 'Approved'")
    
    new_body = body.replace(
        'cur.execute("SELECT id, name FROM ngos WHERE status = \'Approved\'")',
        '''
        cur.execute("SELECT lat, lon FROM hotels WHERE id = ?", (hotel_id,))
        hotel_data = cur.fetchone()
        
        cur.execute("SELECT id, name, lat, lon FROM ngos WHERE status = 'Approved'")
        ngos_raw = cur.fetchall()
        
        ngos = []
        for n in ngos_raw:
            dist = calculate_distance(hotel_data['lat'], hotel_data['lon'], n['lat'], n['lon'])
            ngos.append({'id': n['id'], 'name': n['name'], 'dist': dist})
        
        ngos.sort(key=lambda x: x['dist'])
        '''
    )
    
    # In the POST section, we need to handle "Nearest" logic.
    # if ngo_id == 'Nearest': ngo_id = ngos[0]['id']
    post_logic = '''
        if ngo_id == 'Nearest' and ngos:
            ngo_id = ngos[0]['id']
    '''
    
    # Inject post_logic before "cur.execute("SELECT * FROM predictions WHERE id = ?"
    new_body = new_body.replace('cur.execute("SELECT * FROM predictions WHERE id = ?", (prediction_id,))', post_logic + '\n        cur.execute("SELECT * FROM predictions WHERE id = ?", (prediction_id,))')
    
    return content[:match.start()] + f"def alerts():{new_body}{ret_stmt}" + content[match.end():]

new_content = replace_alerts_func(content)
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)
