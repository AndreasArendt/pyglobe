import numpy as np
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

def wgs2tile(lat__deg, lon__deg):
    '''Spherical to Mercator projection'''
    x = (lon__deg + 180) / 360
    y = 1 - (np.log(np.tan(np.pi / 4 + np.deg2rad(lat__deg) / 2)) / np.pi + 1) / 2

    return x, y

def getXYZfromUrl(url):
    regResult = re.findall(f'^{OSM_BASE_URL}/(\d+)/(\d+)/(\d+)\.png$', url)
    x = regResult[0][0]
    y = regResult[0][1]
    z = regResult[0][2]

    return x, y, z

def getTileUrl(x, y, z=10):
    assert z < 20 and z >= 0, 'zoom levels need to be between 0 and 19'

    n = 2**z
    x = int(np.floor(x * n))
    y = int(np.floor(y * n))
    z = int(z)

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
