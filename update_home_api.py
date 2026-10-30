import os
import sqlite3

def run():
    # 1. Add route to app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()

    api_code = '''
@app.route('/api/public_directory')
def public_directory():
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get up to 20 Approved Hotels
        cur.execute('SELECT hotel_name as name, address as location, hotel_type as type FROM hotels LIMIT 20')
        hotels = [dict(row) for row in cur.fetchall()]
        
        # Get up to 20 Approved NGOs
        cur.execute('SELECT name, location FROM ngos WHERE status = "Approved" LIMIT 20')
        ngos = [dict(row) for row in cur.fetchall()]
        
        # Add a mock 'focus' field for NGOs if needed by the frontend, or just use location
        for n in ngos:
            n['focus'] = 'Food Rescue & Redistribution'
            
        from flask import jsonify
        return jsonify({'hotels': hotels, 'ngos': ngos})
'''

    if '/api/public_directory' not in app_content:
        with open('app.py', 'a', encoding='utf-8') as f:
            f.write('\n' + api_code + '\n')

    # 2. Modify static/js/home.js
    js_path = 'static/js/home.js'
    with open(js_path, 'r', encoding='utf-8') as f:
        js_content = f.read()

    old_fetch_code = '''  // Simulate a network request
  const fetchDirectoryData = () => {
    if (dataLoaded) return;
    
    setTimeout(() => {
      // Hide spinner
      spinner.classList.add("hidden");
      
      // Populate Hotels Grid
      const hotelsGrid = document.getElementById("hotels-list");
      mockDatabase.hotels.forEach(hotel => {
        hotelsGrid.innerHTML += createCard(hotel, "ri-map-pin-2-line");
      });
      
      // Populate NGOs Grid
      const ngosGrid = document.getElementById("ngos-list");
      mockDatabase.ngos.forEach(ngo => {
        ngosGrid.innerHTML += createCard(ngo, "ri-map-pin-2-line");
      });
      
      // Show default active tab
      const activeTabId = document.querySelector(".tab-btn.active").getAttribute("data-target");
      document.getElementById(activeTabId).classList.remove("hidden");
      
      dataLoaded = true;
    }, 1500); // 1.5s delay to mimic network latency
  };'''

    new_fetch_code = '''  // Fetch live network request
  const fetchDirectoryData = async () => {
    if (dataLoaded) return;
    
    try {
      const response = await fetch('/api/public_directory');
      const liveData = await response.json();
      
      // Hide spinner
      spinner.classList.add("hidden");
      
      // Populate Hotels Grid
      const hotelsGrid = document.getElementById("hotels-list");
      liveData.hotels.forEach(hotel => {
        hotelsGrid.innerHTML += createCard(hotel, "ri-map-pin-2-line");
      });
      
      // Populate NGOs Grid
      const ngosGrid = document.getElementById("ngos-list");
      liveData.ngos.forEach(ngo => {
        ngosGrid.innerHTML += createCard(ngo, "ri-map-pin-2-line");
      });
      
      // Show default active tab
      const activeTabId = document.querySelector(".tab-btn.active").getAttribute("data-target");
      document.getElementById(activeTabId).classList.remove("hidden");
      
      dataLoaded = true;
    } catch (err) {
      spinner.innerHTML = '<p style="color: #e74c3c;">Error loading directory data.</p>';
    }
  };'''

    if 'fetchDirectoryData = () =>' in js_content:
        js_content = js_content.replace(old_fetch_code, new_fetch_code)
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print("Updated js_content successfully")
    else:
        print("Could not find old_fetch_code in js_content")

if __name__ == '__main__':
    run()
