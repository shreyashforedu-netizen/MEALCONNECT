import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_map_api_block = '''
@app.route('/api/map_data')
@login_required
def map_data():
    hotel_id = session.get('hotel_id')
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get Hotel Data
        cur.execute("""
            SELECT h.id, h.hotel_name, h.lat, h.lon, h.hotel_type, h.address, 
                   (SELECT SUM(reserved_kg) FROM alerts WHERE hotel_id = h.id AND status = 'Collected') as total_donated,
                   (SELECT status FROM alerts WHERE hotel_id = h.id AND status IN ('Pending', 'Accepted') LIMIT 1) as active_alert
            FROM hotels h WHERE h.id = ?
        """, (hotel_id,))
        hotel_row = cur.fetchone()
        
        if not hotel_row or hotel_row['lat'] is None or hotel_row['lon'] is None:
            hotel_data = {'id': hotel_id, 'name': session.get('hotel_name', 'Unknown'), 'lat': None, 'lon': None}
        else:
            total = hotel_row['total_donated'] or 0
            badge = 'Gold' if total > 500 else 'Silver' if total > 100 else 'Bronze' if total > 0 else 'New'
            hotel_data = {
                'id': hotel_row['id'],
                'name': hotel_row['hotel_name'],
                'lat': hotel_row['lat'],
                'lon': hotel_row['lon'],
                'type': hotel_row['hotel_type'] or 'Hotel',
                'address': hotel_row['address'],
                'rating': 4.5,
                'total_donated': total,
                'badge': badge,
                'active_alert': hotel_row['active_alert']
            }
            
        # Get NGOs Data
        cur.execute("""
            SELECT n.id, n.name, n.contact_person, n.phone, n.email, n.location, n.lat, n.lon,
                   (SELECT SUM(reserved_kg) FROM alerts WHERE ngo_id = n.id AND status = 'Collected') as total_collected
            FROM ngos n WHERE n.status = 'Approved' AND n.lat IS NOT NULL AND n.lon IS NOT NULL
        """)
        ngos_rows = cur.fetchall()
        
    ngo_list = []
    for ngo in ngos_rows:
        dist = None
        eta = None
        if hotel_data['lat'] is not None and hotel_data['lon'] is not None:
            dist = calculate_distance(hotel_data['lat'], hotel_data['lon'], ngo['lat'], ngo['lon'])
            if dist is not None:
                eta = round(dist * 2) # Roughly 2 mins per km in city traffic
                
        ngo_list.append({
            'id': ngo['id'],
            'name': ngo['name'],
            'contact_person': ngo['contact_person'],
            'phone': ngo['phone'],
            'email': ngo['email'],
            'location': ngo['location'],
            'lat': ngo['lat'],
            'lon': ngo['lon'],
            'rating': 4.8,
            'total_collected': ngo['total_collected'] or 0,
            'distance_km': dist,
            'eta_mins': eta
        })
        
    return jsonify({
        'hotel': hotel_data,
        'ngos': sorted(ngo_list, key=lambda x: x['distance_km'] if x['distance_km'] is not None else 999999)
    })

@app.route('/api/ngo_map_data')
@ngo_login_required
def ngo_map_data():
    ngo_id = session.get('ngo_id')
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get NGO Data
        cur.execute("SELECT id, name, lat, lon FROM ngos WHERE id = ?", (ngo_id,))
        ngo_row = cur.fetchone()
        
        ngo_data = {'name': 'Unknown', 'lat': None, 'lon': None}
        if ngo_row and ngo_row['lat'] is not None and ngo_row['lon'] is not None:
            ngo_data = {
                'id': ngo_row['id'],
                'name': ngo_row['name'],
                'lat': ngo_row['lat'],
                'lon': ngo_row['lon']
            }
        
        # Get Active Hotels
        cur.execute("""
            SELECT h.id, h.hotel_name, h.hotel_type, h.address, h.lat, h.lon, h.phone, 
                   a.id as alert_id, a.reserved_kg, a.status, a.created_at
            FROM alerts a
            JOIN hotels h ON a.hotel_id = h.id
            WHERE (a.ngo_id = ? OR a.ngo_id IS NULL) AND a.status = 'Pending' AND h.lat IS NOT NULL AND h.lon IS NOT NULL
        """, (ngo_id,))
        active_hotels = cur.fetchall()
        
    hotel_list = []
    for h in active_hotels:
        dist = None
        eta = None
        if ngo_data['lat'] is not None and ngo_data['lon'] is not None:
            dist = calculate_distance(ngo_data['lat'], ngo_data['lon'], h['lat'], h['lon'])
            if dist is not None:
                eta = round(dist * 2)
                
        hotel_list.append({
            'id': h['id'],
            'name': h['hotel_name'],
            'type': h['hotel_type'] or 'Hotel',
            'address': h['address'],
            'contact': h['phone'],
            'lat': h['lat'],
            'lon': h['lon'],
            'alert_id': h['alert_id'],
            'reserved_kg': h['reserved_kg'],
            'status': h['status'],
            'created_at': h['created_at'],
            'distance_km': dist,
            'eta_mins': eta
        })
        
    return jsonify({
        'ngo': ngo_data,
        'hotels': hotel_list
    })
'''

# Use regex to replace the existing map_data and ngo_map_data blocks
pattern = re.compile(r"@app\.route\('/api/map_data'\).*?return jsonify\([^)]+\)\s*\n", re.DOTALL)
content = pattern.sub('', content)

pattern2 = re.compile(r"@app\.route\('/api/ngo_map_data'\).*?return jsonify\([^)]+\)\s*\n", re.DOTALL)
content = pattern2.sub('', content)

# Inject the new blocks before the map() route
pattern3 = re.compile(r"@app\.route\('/map'\)")
content = pattern3.sub(new_map_api_block + "\n@app.route('/map')", content)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
