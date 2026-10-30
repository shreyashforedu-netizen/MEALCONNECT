import os
import re

def update():
    # --- 1. UPDATE app.py ---
    with open('app.py', 'r', encoding='utf-8') as f:
        app_code = f.read()
        
    old_sql = """          # Get NGOs Data
          cur.execute(\"\"\"
              SELECT n.id, n.name, n.contact_person, n.phone, n.email, n.location, n.lat, n.lon,
                     (SELECT SUM(reserved_kg) FROM alerts WHERE ngo_id = n.id AND status = 'Collected') as total_collected
              FROM ngos n WHERE n.status = 'Approved' AND n.lat IS NOT NULL AND n.lon IS NOT NULL
          \"\"\")"""
          
    new_sql = """          # Get NGOs Data
          cur.execute(\"\"\"
              SELECT n.id, n.name, n.contact_person, n.phone, n.email, n.location, n.lat, n.lon,
                     (SELECT SUM(reserved_kg) FROM alerts WHERE ngo_id = n.id AND status = 'Collected') as total_collected,
                     (SELECT status FROM alerts WHERE hotel_id = ? AND (ngo_id = n.id OR ngo_id IS NULL) AND status IN ('Pending', 'Accepted') LIMIT 1) as active_alert
              FROM ngos n WHERE n.status = 'Approved' AND n.lat IS NOT NULL AND n.lon IS NOT NULL
          \"\"\", (hotel_id,))"""
          
    app_code = app_code.replace(old_sql, new_sql)
    
    old_dict = """              'location': ngo['location'],
              'lat': ngo['lat'],
              'lon': ngo['lon'],
              'total_collected': ngo['total_collected'] or 0,
              'rating': 4.8,
              'distance_km': dist,
              'eta_mins': eta
          })"""
          
    new_dict = """              'location': ngo['location'],
              'lat': ngo['lat'],
              'lon': ngo['lon'],
              'total_collected': ngo['total_collected'] or 0,
              'rating': 4.8,
              'distance_km': dist,
              'eta_mins': eta,
              'active_alert': ngo['active_alert']
          })"""
          
    app_code = app_code.replace(old_dict, new_dict)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code)


    # --- 2. UPDATE map.html ---
    with open('templates/map.html', 'r', encoding='utf-8') as f:
        map_code = f.read()
        
    old_js = """                // Draw NGOs
                allNGOs.forEach(ngo => {
                    const m = L.marker([ngo.lat, ngo.lon], { icon: createIcon('NGO', false, false) })
                        .bindPopup(`"""
                        
    new_js = """                // Draw NGOs
                allNGOs.forEach(ngo => {
                    const hasActiveAlert = ngo.active_alert ? true : false;
                    const m = L.marker([ngo.lat, ngo.lon], { icon: createIcon('NGO', false, hasActiveAlert) })
                        .bindPopup(`"""
                        
    map_code = map_code.replace(old_js, new_js)
    
    with open('templates/map.html', 'w', encoding='utf-8') as f:
        f.write(map_code)

if __name__ == '__main__':
    update()
