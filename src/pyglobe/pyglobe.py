import math
import requests
from ratelimit import limits, sleep_and_retry
import io
import os
import re
from PIL import Image

OSM_BASE_URL = 'https://tile.openstreetmap.org'
CACHE_PATH = os.path.abspath(os.curdir +  '/data')

@sleep_and_retry
@limits(calls=1, period=5)
def check_limit():
    ''' Empty function just to check for calls to API '''
    return

def XYZ2Wgs(x,y,z):
    R =  6378137.0
    lat__deg = math.degrees(2 * math.atan(math.exp (y / R)) - math.pi / 2.0)
    lon__deg = math.degrees(x / R)

    return lat__deg, lon__deg

def wgs2tile(lat__deg, lon__deg, zoom=10):
    '''Spherical to Mercator projection'''
    assert zoom < 20 and zoom >= 0, 'zoom levels need to be between 0 and 19'

    x = (lon__deg + 180) / 360
    y = 1 - (math.log(math.tan(math.pi / 4 + math.radians(lat__deg) / 2)) / math.pi + 1) / 2

    n = 2**zoom
    x = int(math.floor(x * n))
    y = int(math.floor(y * n))

    return x, y

def getNextTiles(x,y):
    #(2x  , 2y)   (2x  , 2y+1)
    #(2x+1, 2y)   (2x+1, 2y+1)
    a = 1

def getXYZfromUrl(url):
    regResult = re.findall(f'^{OSM_BASE_URL}/(\d+)/(\d+)/(\d+)\.png$', url)
    x = int(regResult[0][0])
    y = int(regResult[0][1])
    z = int(regResult[0][2])

    return x, y, z

def getTileUrl(x, y, z=10):
    return f'{OSM_BASE_URL}/{z}/{x}/{y}.png'

def getChachePath(x, y, z):
    return f'{CACHE_PATH}/{x}_{y}_{z}.tile'

def getCachedTile(url):
    x, y, z = getXYZfromUrl(url)
    tilePath = getChachePath(x, y, z)

    if os.path.exists(tilePath):
        with open(tilePath, mode='rb') as file:
            tile = file.read()
        return tile
    else:
        return None

def cacheTile(data, url):
    x, y, z = getXYZfromUrl(url)
    tilePath = getChachePath(x, y, z)

    with open(tilePath, mode='wb') as file:
        file.write(data.getbuffer())

def getTileBytes(url, caching=True):
    if caching:
        tile = getCachedTile(url)

        if tile is not None:
            return io.BytesIO(tile)

    # rate limit calls
    check_limit()

    headers = {
        'User-Agent': 'pyglobe 1.0',
        'From': 'andi.arendt@icloud.com'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    tileData = io.BytesIO(response.content)
    if caching:
        cacheTile(tileData, url)

    return tileData

def getTileLatLon(lat__deg, lon__deg, zoom=10):
    x, y = map.wgs2tile(lat__deg, lon__deg)
    tileUrl = map.getTileUrl(x=x, y=y, z=zoom)
    return getTileBytes(tileUrl)

def getTileXY(x, y, zoom=10):
    tileUrl = map.getTileUrl(x=x, y=y, z=zoom)
    return getTileBytes(tileUrl)
