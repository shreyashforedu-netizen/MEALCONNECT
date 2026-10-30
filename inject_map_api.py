import os

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

map_api_block = '''
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on the earth."""
    if None in (lat1, lon1, lat2, lon2):
        return float('inf')
        
    R = 6371  # Radius of the earth in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    
    a = (math.sin(dLat/2) * math.sin(dLat/2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dLon/2) * math.sin(dLon/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return round(R * c, 2)

@app.route('/api/map_data')
@login_required
def map_data():
    hotel_id = session['hotel_id']
    with get_db() as conn:
        cur = conn.cursor()
        
        cur.execute("SELECT hotel_name, lat, lon FROM hotels WHERE id = ?", (hotel_id,))
        hotel = cur.fetchone()
        
        cur.execute("SELECT id, name, contact_person, phone, lat, lon FROM ngos WHERE status = 'Approved'")
        ngos = cur.fetchall()
        
    ngo_list = []
    for ngo in ngos:
        dist = calculate_distance(hotel['lat'], hotel['lon'], ngo['lat'], ngo['lon'])
        ngo_list.append({
            'id': ngo['id'],
            'name': ngo['name'],
            'contact': f"{ngo['contact_person']} ({ngo['phone']})",
            'lat': ngo['lat'],
            'lon': ngo['lon'],
            'distance_km': dist
        })
        
    return jsonify({
        'hotel': {
            'name': hotel['hotel_name'] if hotel else 'Unknown',
            'lat': hotel['lat'] if hotel else None,
            'lon': hotel['lon'] if hotel else None
        },
        'ngos': sorted(ngo_list, key=lambda x: x['distance_km'])
    })

@app.route('/api/ngo_map_data')
@ngo_login_required
def ngo_map_data():
    ngo_id = session['ngo_id']
    with get_db() as conn:
        cur = conn.cursor()
        
        cur.execute("SELECT name, lat, lon FROM ngos WHERE id = ?", (ngo_id,))
        ngo = cur.fetchone()
        
        # Get active alerts for hotels
        cur.execute("""
            SELECT h.id, h.hotel_name, h.lat, h.lon, h.phone, a.reserved_kg 
            FROM alerts a
            JOIN hotels h ON a.hotel_id = h.id
            WHERE (a.ngo_id = ? OR a.ngo_id IS NULL) AND a.status = 'Pending'
        """, (ngo_id,))
        active_hotels = cur.fetchall()
        
    hotel_list = []
    for h in active_hotels:
        hotel_list.append({
            'id': h['id'],
            'name': h['hotel_name'],
            'contact': h['phone'],
            'lat': h['lat'],
            'lon': h['lon'],
            'reserved_kg': h['reserved_kg']
        })
        
    return jsonify({
        'ngo': {
            'name': ngo['name'] if ngo else 'Unknown',
            'lat': ngo['lat'] if ngo else None,
            'lon': ngo['lon'] if ngo else None
        },
        'hotels': hotel_list
    })

@app.route('/map')
@login_required
def live_map():
    return render_template('map.html', hotel_name=session.get('hotel_name'), hotel_id=session['hotel_id'])
'''

if 'def calculate_distance' not in content:
    parts = content.split("if __name__ == '__main__':")
    if len(parts) == 2:
        new_content = parts[0] + map_api_block + "\nif __name__ == '__main__':" + parts[1]
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully injected Map API")
