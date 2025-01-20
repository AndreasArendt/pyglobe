import pyglobe.pyglobe as map

def getTileGrid(width, height, lat_deg, lon_deg, zoom=10):
    map.getTileLatLon(lat_deg, lon_deg)
