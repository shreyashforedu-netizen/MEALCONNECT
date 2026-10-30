with open('templates/map.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_str = 'body:not(.light-theme) .leaflet-tile-pane { filter: invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%); }'
new_str = 'html[data-theme="dark"] .leaflet-tile-pane, :root:not([data-theme="light"]) .leaflet-tile-pane { filter: invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%); }'
html = html.replace(old_str, new_str)

with open('templates/map.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("done")
