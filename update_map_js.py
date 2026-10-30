import re

with open('templates/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_js = '''
    <script>
        document.addEventListener('DOMContentLoaded', async () => {
            const mapContainer = document.getElementById('map');
            try {
                const response = await fetch('/api/map_data');
                if (!response.ok) throw new Error("API returned " + response.status);
                const data = await response.json();
                
                const mapCenter = data.hotel && data.hotel.lat ? [data.hotel.lat, data.hotel.lon] : [20.5937, 78.9629];
                const map = L.map('map').setView(mapCenter, 12);
                
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap'
                }).addTo(map);

                if (data.hotel && data.hotel.lat && data.hotel.lon) {
                    L.marker([data.hotel.lat, data.hotel.lon])
                     .addTo(map)
                     .bindPopup(`<b>Your Hotel: ${data.hotel.name}</b>`)
                     .openPopup();
                }

                if (data.ngos && data.ngos.length > 0) {
                    const greenIcon = new L.Icon({
                      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                      iconSize: [25, 41],
                      iconAnchor: [12, 41],
                      popupAnchor: [1, -34]
                    });

                    data.ngos.forEach(ngo => {
                        if (ngo.lat && ngo.lon) {
                            L.marker([ngo.lat, ngo.lon], {icon: greenIcon})
                             .addTo(map)
                             .bindPopup(`<b>${ngo.name}</b><br>Contact: ${ngo.contact}`);
                        }
                    });
                }
            } catch (error) {
                mapContainer.innerHTML = "<div style='color:red; padding:2rem; background:black; height:100%; border-radius:12px;'><h3>Map Error:</h3><p>" + error.message + "</p></div>";
            }
        });
    </script>
'''

content = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\'.*?</script>', new_js.strip(), content, flags=re.DOTALL)

with open('templates/map.html', 'w', encoding='utf-8') as f:
    f.write(content)
