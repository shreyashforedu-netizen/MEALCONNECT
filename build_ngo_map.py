ngo_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NGO Dashboard - Meal Connect</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@400;600&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/home.css') }}">
    
    <!-- Leaflet & Plugins -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.Default.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine@latest/dist/leaflet-routing-machine.css" />
    
    <script src="{{ url_for('static', filename='js/theme.js') }}"></script>
    <style>
      body { display: flex; height: 100vh; overflow: hidden; background: var(--bg-color); }
      .sidebar { width: 280px; background: rgba(6, 11, 8, 0.95); border-right: 1px solid var(--surface-border); padding: 2rem; display: flex; flex-direction: column; z-index: 1000; flex-shrink: 0; }
      .sidebar-logo { margin-bottom: 3rem; font-size: 1.5rem; }
      .nav-menu { list-style: none; display: flex; flex-direction: column; gap: 0.5rem; flex-grow: 1; }
      .nav-item { padding: 1rem; border-radius: 12px; color: var(--text-muted); text-decoration: none; display: flex; align-items: center; gap: 1rem; transition: var(--transition); font-weight: 500; }
      .nav-item:hover, .nav-item.active { background: rgba(46,204,113,0.1); color: var(--primary); }
      
      .main-content { flex-grow: 1; display: flex; flex-direction: column; position: relative; overflow: hidden; }
      
      .top-bar { 
          display: flex; justify-content: space-between; align-items: center; 
          padding: 1.5rem 2rem; border-bottom: 1px solid var(--surface-border); background: var(--surface-color); z-index: 10;
      }
      
      .map-layout { display: flex; flex-grow: 1; overflow: hidden; position: relative; }
      #map { flex-grow: 1; height: 100%; z-index: 1; background: #222; }
      
      /* Control Panel */
      .control-panel {
          position: absolute; top: 1rem; right: 1rem; width: 320px; z-index: 1000;
          background: var(--surface-color); border: 1px solid var(--surface-border);
          border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.2); padding: 1rem;
          max-height: calc(100vh - 120px); overflow-y: auto; backdrop-filter: blur(10px);
      }
      
      /* Legend */
      .legend {
          position: absolute; bottom: 2rem; left: 1rem; z-index: 1000;
          background: rgba(6, 11, 8, 0.9); border: 1px solid var(--surface-border);
          border-radius: 8px; padding: 1rem; font-size: 0.85rem; backdrop-filter: blur(5px);
      }
      .legend-item { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
      
      /* Custom Markers */
      .custom-marker { display: flex; justify-content: center; align-items: center; width: 36px; height: 36px; border-radius: 50%; color: white; font-size: 1.2rem; box-shadow: 0 4px 10px rgba(0,0,0,0.3); border: 2px solid white; }
      .marker-hotel { background: #f39c12; }
      .marker-ngo { background: #2ecc71; width: 44px; height: 44px; font-size: 1.5rem; animation: pulse-green 2s infinite; }
      .marker-alert { animation: pulse-red 1.5s infinite; border-color: #e74c3c; }
      
      @keyframes pulse-green {
          0% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7); }
          70% { box-shadow: 0 0 0 15px rgba(46, 204, 113, 0); }
          100% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0); }
      }
      @keyframes pulse-red {
          0% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.8); }
          70% { box-shadow: 0 0 0 20px rgba(231, 76, 60, 0); }
          100% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); }
      }
      
      /* Popups & Tooltips */
      .leaflet-popup-content-wrapper { background: var(--surface-color); color: var(--text-color); border: 1px solid var(--surface-border); border-radius: 12px; }
      .leaflet-popup-tip { background: var(--surface-color); }
      .leaflet-tooltip { background: rgba(0,0,0,0.7); border: none; color: white; font-weight: 500; font-family: var(--font-body); border-radius: 4px; box-shadow: none; }
      .leaflet-tooltip-left::before, .leaflet-tooltip-right::before { border-color: transparent; }
      
      .popup-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem; }
      .popup-title { font-size: 1.1rem; font-family: var(--font-display); font-weight: 600; margin: 0; color: #fff; }
      .popup-body { font-size: 0.9rem; line-height: 1.4; color: var(--text-muted); }
      .popup-actions { display: flex; gap: 0.5rem; margin-top: 1rem; }
      
      /* Nearest Panel */
      .nearest-panel { margin-top: 1rem; border-top: 1px solid var(--surface-border); padding-top: 1rem; }
      .nearest-card { background: rgba(255,255,255,0.05); padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem; cursor: pointer; transition: 0.2s; border: 1px solid transparent; }
      .nearest-card:hover { background: rgba(231,76,60,0.1); border-color: #e74c3c; }
      .card-title { display: flex; justify-content: space-between; font-weight: 600; color: #fff; }
      
      /* Filters */
      .filter-group { margin-bottom: 1rem; }
      
      /* Mobile */
      @media (max-width: 768px) {
          body { flex-direction: column; }
          .sidebar { display: none; }
          .control-panel { 
              top: auto; bottom: 0; right: 0; width: 100%; border-radius: 20px 20px 0 0; 
              max-height: 50vh; padding-bottom: 2rem; border-bottom: none; border-right: none; border-left: none;
          }
          .legend { display: none; }
      }
    </style>
</head>
<body>
    <div class="sidebar glass">
      <a href="{{ url_for('index') }}" class="sidebar-logo nav-logo" style="text-decoration:none; color:inherit; display:flex; align-items:center;">
        <i class="ri-leaf-line" style="margin-right: 8px;"></i> Meal Connect
      </a>
      <ul class="nav-menu">
        <a href="#" class="nav-item active"><i class="ri-dashboard-line"></i> Dashboard</a>
        <a href="#" class="nav-item"><i class="ri-user-line"></i> Profile</a>
        <a href="{{ url_for('ngo_logout') }}" class="btn btn-outline" style="width: 100%; border-color: rgba(231,76,60,0.5); color: #ff6b6b; margin-top: auto;">
          <i class="ri-logout-box-r-line"></i> Logout
        </a>
      </ul>
    </div>

    <div class="main-content">
      <div class="top-bar">
        <div class="hotel-info">
          <h1 style="font-size: 1.5rem; margin: 0;">NGO Dashboard</h1>
          <span style="font-size: 0.85rem; color: var(--text-muted);"><i class="ri-heart-3-line"></i> {{ session.get('ngo_id', '') }}</span>
        </div>
        <div style="display: flex; gap: 1rem;">
            <button id="theme-toggle" class="btn btn-outline btn-sm" style="border:none; font-size:1.2rem; padding:0.5rem;" title="Toggle Theme">
              <i id="theme-toggle-icon" class="ri-moon-line"></i>
            </button>
        </div>
      </div>

      <div class="map-layout">
        <div id="map"></div>
        
        <div class="control-panel glass">
            <div class="filter-group" style="display:flex; gap:0.5rem;">
                <button class="btn btn-primary btn-sm" id="btn-locate" style="flex-grow:1;"><i class="ri-focus-3-line"></i> Locate Me</button>
                <button class="btn btn-outline btn-sm" id="btn-reset" title="Reset View"><i class="ri-refresh-line"></i></button>
                <button class="btn btn-outline btn-sm" id="btn-clear-route" title="Clear Route" style="display:none; border-color:#e74c3c; color:#e74c3c;"><i class="ri-route-line"></i> Clear</button>
            </div>
            
            <div class="nearest-panel" id="nearest-panel">
                <h4 style="margin-bottom:1rem; color:#fff;">Active Food Alerts Nearby</h4>
                <div id="nearest-list">Loading...</div>
            </div>
        </div>
        
        <div class="legend glass">
            <div class="legend-item"><div class="custom-marker marker-ngo" style="width:24px; height:24px; font-size:0.8rem; animation:none;"><i class="ri-heart-3-fill"></i></div> My NGO</div>
            <div class="legend-item"><div class="custom-marker marker-hotel marker-alert" style="width:24px; height:24px; font-size:0.8rem;"><i class="ri-hotel-fill"></i></div> Active Alert</div>
        </div>
      </div>
    </div>

    <!-- Leaflet & Scripts -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/leaflet.markercluster.js"></script>
    <script src="https://unpkg.com/leaflet-routing-machine@latest/dist/leaflet-routing-machine.js"></script>
    
    <script>
        document.addEventListener('DOMContentLoaded', async () => {
            const mapContainer = document.getElementById('map');
            let map, markers, routeControl;
            let myNgo = null;
            let activeHotels = [];
            
            // Tiles
            const tiles = {
                light: L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', { attribution: '© OpenStreetMap, © CartoDB' }),
                dark: L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { attribution: '© OpenStreetMap, © CartoDB' })
            };

            const createIcon = (type, isMe, hasAlert) => {
                let iconClass = 'ri-hotel-fill';
                let bgClass = 'marker-hotel';
                if (type === 'NGO') { iconClass = 'ri-heart-3-fill'; bgClass = 'marker-ngo'; }
                
                let extraClass = '';
                if (isMe) { bgClass = 'marker-ngo'; iconClass = 'ri-heart-3-fill'; }
                else if (hasAlert) { extraClass = 'marker-alert'; }
                
                return L.divIcon({
                    html: `<div class="custom-marker ${bgClass} ${extraClass}"><i class="${iconClass}"></i></div>`,
                    className: 'custom-div-icon',
                    iconSize: [36, 36],
                    iconAnchor: [18, 18],
                    popupAnchor: [0, -18]
                });
            };

            try {
                const response = await fetch('/api/ngo_map_data');
                if (!response.ok) throw new Error("API Error " + response.status);
                const data = await response.json();
                
                myNgo = data.ngo;
                activeHotels = data.hotels;
                
                const center = (myNgo && myNgo.lat) ? [myNgo.lat, myNgo.lon] : [20.5937, 78.9629];
                map = L.map('map').setView(center, 13);
                
                const isDark = document.body.classList.contains('light-theme') ? false : true;
                tiles[isDark ? 'dark' : 'light'].addTo(map);
                
                markers = L.markerClusterGroup({
                    maxClusterRadius: 40,
                    spiderfyOnMaxZoom: true,
                    polygonOptions: { fillOpacity: 0.2, color: '#e74c3c', weight: 1 }
                });

                // Draw My NGO
                if (myNgo && myNgo.lat) {
                    const m = L.marker([myNgo.lat, myNgo.lon], { icon: createIcon('NGO', true, false), zIndexOffset: 1000 })
                        .bindPopup(`
                            <div class="popup-header">
                                <h3 class="popup-title">My NGO: ${myNgo.name}</h3>
                            </div>
                        `)
                        .bindTooltip(myNgo.name, { permanent: true, direction: 'bottom', offset: [0, 15] });
                    map.addLayer(m);
                }

                // Draw Active Hotels
                activeHotels.forEach(h => {
                    const m = L.marker([h.lat, h.lon], { icon: createIcon('Hotel', false, true) })
                        .bindPopup(`
                            <div class="popup-header">
                                <h3 class="popup-title">${h.name}</h3>
                                <span style="color:#e74c3c; font-weight:bold; animation: pulse 1s infinite;"><i class="ri-alert-fill"></i> Pending</span>
                            </div>
                            <div class="popup-body">
                                <div style="font-size:1.1rem; font-weight:bold; color:var(--text-color);"><i class="ri-restaurant-line"></i> ${h.reserved_kg} kg available</div>
                                <div><i class="ri-phone-line"></i> <a href="tel:${h.contact}" style="color:var(--primary)">${h.contact}</a></div>
                                <div><i class="ri-map-pin-line"></i> ${h.address}</div>
                                <div style="margin-top:0.5rem; padding-top:0.5rem; border-top:1px solid rgba(255,255,255,0.1);">
                                    <i class="ri-truck-line"></i> ${h.distance_km} km away (~${h.eta_mins} mins)
                                </div>
                            </div>
                            <div class="popup-actions">
                                <form action="/accept_alert/${h.alert_id}" method="POST" style="flex:1;">
                                    <button type="submit" class="btn btn-primary btn-sm" style="width:100%;"><i class="ri-check-line"></i> Accept</button>
                                </form>
                                <button class="btn btn-outline btn-sm route-btn" data-lat="${h.lat}" data-lon="${h.lon}" style="flex:1;"><i class="ri-route-line"></i> Route</button>
                            </div>
                        `)
                        .bindTooltip(h.name, { permanent: true, direction: 'bottom', offset: [0, 15] });
                    
                    markers.addLayer(m);
                });

                map.addLayer(markers);
                
                map.on('zoomend', () => {
                    const z = map.getZoom();
                    document.querySelectorAll('.leaflet-tooltip').forEach(el => {
                        el.style.opacity = z < 12 ? '0' : '1';
                        el.style.pointerEvents = z < 12 ? 'none' : 'auto';
                    });
                });
                
                const renderNearest = () => {
                    const list = document.getElementById('nearest-list');
                    if (activeHotels.length === 0) { list.innerHTML = '<div style="color:var(--text-muted);">No active alerts nearby.</div>'; return; }
                    
                    const sorted = activeHotels.sort((a,b) => a.distance_km - b.distance_km).slice(0, 5);
                    list.innerHTML = sorted.map((h) => `
                        <div class="nearest-card" onclick="flyToNgo(${h.lat}, ${h.lon})">
                            <div class="card-title">
                                <span><i class="ri-hotel-fill"></i> ${h.name}</span>
                                <span style="color:#e74c3c; font-size:0.85rem;">${h.reserved_kg} kg</span>
                            </div>
                            <div style="color:var(--text-muted); font-size:0.8rem; margin-top:0.2rem;"><i class="ri-truck-line"></i> ${h.distance_km} km • ETA: ${h.eta_mins} mins</div>
                        </div>
                    `).join('');
                };
                renderNearest();

                window.flyToNgo = (lat, lon) => { map.flyTo([lat, lon], 16); };

                // Routing
                document.addEventListener('click', (e) => {
                    const btn = e.target.closest('.route-btn');
                    if (btn) {
                        if (!myNgo || !myNgo.lat) return alert("Your NGO location is missing.");
                        const lat = btn.getAttribute('data-lat');
                        const lon = btn.getAttribute('data-lon');
                        
                        if (routeControl) map.removeControl(routeControl);
                        
                        routeControl = L.Routing.control({
                            waypoints: [ L.latLng(myNgo.lat, myNgo.lon), L.latLng(lat, lon) ],
                            routeWhileDragging: false,
                            showAlternatives: false,
                            addWaypoints: false,
                            lineOptions: { styles: [{color: '#e74c3c', weight: 4}] },
                            createMarker: function() { return null; }
                        }).addTo(map);
                        
                        document.getElementById('btn-clear-route').style.display = 'block';
                    }
                });

                document.getElementById('btn-clear-route').addEventListener('click', () => {
                    if (routeControl) { map.removeControl(routeControl); routeControl = null; }
                    document.getElementById('btn-clear-route').style.display = 'none';
                });
                
                document.getElementById('btn-locate').addEventListener('click', () => {
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(pos => {
                            map.flyTo([pos.coords.latitude, pos.coords.longitude], 15);
                        }, () => {
                            if (myNgo && myNgo.lat) map.flyTo([myNgo.lat, myNgo.lon], 15);
                        });
                    }
                });
                
                document.getElementById('btn-reset').addEventListener('click', () => {
                    const bounds = L.latLngBounds([ [myNgo.lat, myNgo.lon] ]);
                    activeHotels.forEach(h => bounds.extend([h.lat, h.lon]));
                    map.fitBounds(bounds, { padding: [50, 50] });
                });

            } catch (err) {
                mapContainer.innerHTML = `<div style="padding:2rem; color:#ff6b6b;"><h3>Map Error</h3><p>${err.message}</p></div>`;
            }
        });
    </script>
</body>
</html>
"""

with open('templates/ngo_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(ngo_html)
