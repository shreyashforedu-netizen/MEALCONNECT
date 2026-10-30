import os

map_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Live Distribution Map - Meal Connect</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@400;600&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/home.css') }}">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
      body { display: flex; height: 100vh; overflow: hidden; background: #060b08; }
      .sidebar { width: 280px; background: rgba(6, 11, 8, 0.95); border-right: 1px solid var(--surface-border); padding: 2rem; display: flex; flex-direction: column; z-index: 10; }
      .sidebar-logo { margin-bottom: 3rem; font-size: 1.5rem; }
      .nav-menu { list-style: none; display: flex; flex-direction: column; gap: 0.5rem; flex-grow: 1; }
      .nav-item { padding: 1rem; border-radius: 12px; color: var(--text-muted); text-decoration: none; display: flex; align-items: center; gap: 1rem; transition: var(--transition); font-weight: 500; }
      .nav-item:hover, .nav-item.active { background: rgba(46,204,113,0.1); color: var(--primary); }
      #map { height: 75vh; width: 100%; border-radius: 12px; z-index: 1; }
    </style>
</head>
<body>
    <div class="sidebar glass">
      <a href="{{ url_for('index') }}" class="sidebar-logo nav-logo" style="text-decoration:none; color:inherit; display:flex; align-items:center;">
        <i class="ri-leaf-line" style="margin-right: 8px;"></i> Meal Connect
      </a>
      <ul class="nav-menu">
        <a href="{{ url_for('dashboard') }}" class="nav-item">
          <i class="ri-dashboard-line"></i> Dashboard
        </a>
        <a href="{{ url_for('food_entry') }}" class="nav-item">
          <i class="ri-edit-box-line"></i> Daily Entry
        </a>
        <a href="{{ url_for('prediction') }}" class="nav-item">
          <i class="ri-line-chart-line"></i> Prediction
        </a>
        <a href="{{ url_for('alerts') }}" class="nav-item">
          <i class="ri-notification-badge-line"></i> Pending Alerts
        </a>
        <a href="{{ url_for('live_map') }}" class="nav-item active">
          <i class="ri-map-pin-line"></i> Live Map
        </a>
        <a href="{{ url_for('history') }}" class="nav-item">
          <i class="ri-history-line"></i> History
        </a>
        <a href="{{ url_for('analytics') }}" class="nav-item">
          <i class="ri-bar-chart-2-line"></i> Analytics
        </a>
        <a href="{{ url_for('profile') }}" class="nav-item">
          <i class="ri-settings-4-line"></i> Settings
        </a>
        <a href="{{ url_for('logout') }}" class="btn btn-outline" style="width: 100%; border-color: rgba(231,76,60,0.5); color: #ff6b6b; margin-top: 2rem;">
          <i class="ri-logout-box-r-line"></i> Logout
        </a>
      </ul>
    </div>

    <div class="main-content">
      <div class="top-bar" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid var(--surface-border);">
        <div class="hotel-info">
          <h1>Live Distribution Map</h1>
          <span class="hotel-id-badge" style="background: rgba(255,255,255,0.1); padding: 0.3rem 0.8rem; border-radius: 50px; font-size: 0.85rem; color: #fff; font-family: monospace;"><i class="ri-building-line"></i> {{ hotel_id }}</span>
        </div>
      </div>

      <div class="panel glass">
        <h2 class="panel-title">Nearby Approved NGOs</h2>
        <div id="map"></div>
      </div>
    </div>

    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', async () => {
            const response = await fetch('/api/map_data');
            const data = await response.json();
            
            const mapCenter = data.hotel.lat ? [data.hotel.lat, data.hotel.lon] : [20.5937, 78.9629];
            const map = L.map('map').setView(mapCenter, 12);
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap'
            }).addTo(map);

            if (data.hotel.lat && data.hotel.lon) {
                L.marker([data.hotel.lat, data.hotel.lon])
                 .addTo(map)
                 .bindPopup(`<b>Your Hotel: ${data.hotel.name}</b>`)
                 .openPopup();
            }

            const greenIcon = new L.Icon({
              iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
              shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
              iconSize: [25, 41],
              iconAnchor: [12, 41],
              popupAnchor: [1, -34],
              shadowSize: [41, 41]
            });

            data.ngos.forEach(ngo => {
                if (ngo.lat && ngo.lon) {
                    L.marker([ngo.lat, ngo.lon], {icon: greenIcon})
                     .addTo(map)
                     .bindPopup(`
                        <b>${ngo.name}</b><br>
                        Distance: ${ngo.distance_km === Infinity ? 'Unknown' : ngo.distance_km + ' km'}<br>
                        Contact: ${ngo.contact}
                     `);
                }
            });
        });
    </script>
</body>
</html>
'''

ngo_login_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>NGO Login - Meal Connect</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/home.css') }}">
</head>
<body style="display:flex; justify-content:center; align-items:center; height:100vh;">
  <div class="glass" style="padding: 3rem; width: 400px; border-radius: 16px;">
    <div style="text-align: center; margin-bottom: 2rem;">
      <h2 style="font-family: 'Outfit'; font-size: 1.8rem; margin-bottom: 0.5rem;">NGO Portal</h2>
      <p style="color: var(--text-muted);">Login to manage food collections</p>
    </div>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div style="padding: 1rem; border-radius: 8px; margin-bottom: 1rem; background: rgba(231, 76, 60, 0.2); color: #e74c3c; border: 1px solid rgba(231, 76, 60, 0.3);">
            {{ message }}
          </div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <form action="{{ url_for('ngo_login') }}" method="POST">
      <div style="margin-bottom: 1.5rem;">
        <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.9rem;">Email Address</label>
        <input type="email" name="email" class="form-input" placeholder="ngo@example.com" required>
      </div>
      <div style="margin-bottom: 2rem;">
        <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.9rem;">Password</label>
        <input type="password" name="password" class="form-input" placeholder="Enter your password" required>
      </div>
      <button type="submit" class="btn btn-primary" style="width: 100%;">Login to NGO Portal</button>
    </form>
    
    <div style="text-align: center; margin-top: 2rem; font-size: 0.9rem; color: var(--text-muted);">
      Don't have an account? <a href="{{ url_for('ngo_signup') }}" style="color: var(--primary); text-decoration: none;">Register NGO</a>
    </div>
  </div>
</body>
</html>
'''

ngo_signup_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>NGO Registration - Meal Connect</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/home.css') }}">
</head>
<body style="display:flex; justify-content:center; align-items:center; min-height:100vh; padding: 2rem;">
  <div class="glass" style="padding: 3rem; width: 500px; border-radius: 16px;">
    <div style="text-align: center; margin-bottom: 2rem;">
      <h2 style="font-family: 'Outfit'; font-size: 1.8rem; margin-bottom: 0.5rem;">NGO Registration</h2>
      <p style="color: var(--text-muted);">Join to collect surplus food</p>
    </div>
    
    <form action="{{ url_for('ngo_signup') }}" method="POST">
      <div style="margin-bottom: 1rem;">
        <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.9rem;">NGO Name</label>
        <input type="text" name="name" class="form-input" required>
      </div>
      <div style="margin-bottom: 1rem;">
        <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.9rem;">Contact Person</label>
        <input type="text" name="contact" class="form-input" required>
      </div>
      <div style="margin-bottom: 1rem;">
        <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.9rem;">Phone</label>
        <input type="text" name="phone" class="form-input" required>
      </div>
      <div style="margin-bottom: 1rem;">
        <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.9rem;">Email</label>
        <input type="email" name="email" class="form-input" required>
      </div>
      <div style="margin-bottom: 1rem;">
        <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.9rem;">Address/Location</label>
        <textarea name="address" class="form-input" required></textarea>
      </div>
      <div style="margin-bottom: 2rem;">
        <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.9rem;">Password</label>
        <input type="password" name="password" class="form-input" required>
      </div>
      <button type="submit" class="btn btn-primary" style="width: 100%;">Register NGO</button>
    </form>
    
    <div style="text-align: center; margin-top: 2rem; font-size: 0.9rem; color: var(--text-muted);">
      Already registered? <a href="{{ url_for('ngo_login') }}" style="color: var(--primary); text-decoration: none;">Login</a>
    </div>
  </div>
</body>
</html>
'''

ngo_dashboard_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>NGO Dashboard - Meal Connect</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@400;600&display=swap" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/home.css') }}">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <style>
    body { display: flex; height: 100vh; overflow: hidden; background: #060b08; }
    .sidebar { width: 280px; background: rgba(6, 11, 8, 0.95); border-right: 1px solid var(--surface-border); padding: 2rem; display: flex; flex-direction: column; z-index: 10; }
    .sidebar-logo { margin-bottom: 3rem; font-size: 1.5rem; }
    .nav-menu { list-style: none; display: flex; flex-direction: column; gap: 0.5rem; flex-grow: 1; }
    .nav-item { padding: 1rem; border-radius: 12px; color: var(--text-muted); text-decoration: none; display: flex; align-items: center; gap: 1rem; transition: var(--transition); font-weight: 500; }
    .nav-item:hover, .nav-item.active { background: rgba(46,204,113,0.1); color: var(--primary); }
    #map { height: 400px; width: 100%; border-radius: 12px; z-index: 1; margin-bottom: 2rem; }
  </style>
</head>
<body>
  <div class="sidebar glass">
    <a href="#" class="sidebar-logo nav-logo" style="text-decoration:none; color:inherit; display:flex; align-items:center;">
      <i class="ri-leaf-line" style="margin-right: 8px;"></i> NGO Portal
    </a>
    <ul class="nav-menu">
      <a href="#" class="nav-item active">
        <i class="ri-dashboard-line"></i> Alerts & Map
      </a>
      <a href="{{ url_for('logout') }}" class="btn btn-outline" style="width: 100%; border-color: rgba(231,76,60,0.5); color: #ff6b6b; margin-top: auto;">
        <i class="ri-logout-box-r-line"></i> Logout
      </a>
    </ul>
  </div>

  <div class="main-content">
    <div class="top-bar" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid var(--surface-border);">
      <div class="hotel-info">
        <h1>Welcome, {{ ngo_name }}</h1>
      </div>
    </div>

    <!-- Map Section -->
    <div class="panel glass">
      <h2 class="panel-title">Nearby Hotels with Active Alerts</h2>
      <div id="map"></div>
    </div>

    <!-- Alerts Table -->
    <div class="panel glass">
      <h2 class="panel-title">Incoming Food Alerts</h2>
      {% if active_alerts %}
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Hotel Name</th>
              <th>Contact</th>
              <th>Available Food (kg)</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {% for a in active_alerts %}
            <tr>
              <td>{{ a.hotel_name }}</td>
              <td>{{ a.phone }}</td>
              <td><span style="color:var(--primary); font-weight:bold;">{{ a.reserved_kg }} kg</span></td>
              <td>
                <form action="{{ url_for('mark_collected') }}" method="POST" style="display:inline;">
                  <input type="hidden" name="alert_id" value="{{ a.id }}">
                  <input type="hidden" name="actual_waste" value="{{ a.reserved_kg }}">
                  <button type="submit" class="btn btn-primary btn-sm">Accept & Collect</button>
                </form>
              </td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
      {% else %}
      <p style="color:var(--text-muted); text-align:center; padding:2rem;">No active alerts at the moment.</p>
      {% endif %}
    </div>
  </div>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
      document.addEventListener('DOMContentLoaded', async () => {
          const response = await fetch('/api/ngo_map_data');
          const data = await response.json();
          
          const mapCenter = data.ngo.lat ? [data.ngo.lat, data.ngo.lon] : [20.5937, 78.9629];
          const map = L.map('map').setView(mapCenter, 12);
          
          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
              attribution: '© OpenStreetMap'
          }).addTo(map);

          if (data.ngo.lat && data.ngo.lon) {
              L.marker([data.ngo.lat, data.ngo.lon])
               .addTo(map)
               .bindPopup(`<b>Your NGO: ${data.ngo.name}</b>`)
               .openPopup();
          }

          const redIcon = new L.Icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
          });

          data.hotels.forEach(hotel => {
              if (hotel.lat && hotel.lon) {
                  L.marker([hotel.lat, hotel.lon], {icon: redIcon})
                   .addTo(map)
                   .bindPopup(`
                      <b>${hotel.name}</b><br>
                      Food Available: ${hotel.reserved_kg} kg<br>
                      Contact: ${hotel.contact}
                   `);
              }
          });
      });
  </script>
</body>
</html>
'''

files = {
    'templates/map.html': map_html,
    'templates/ngo_login.html': ngo_login_html,
    'templates/ngo_signup.html': ngo_signup_html,
    'templates/ngo_dashboard.html': ngo_dashboard_html
}

for filepath, html_content in files.items():
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content.strip())
