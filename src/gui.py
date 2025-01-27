import pyglobe.pyglobe as map
from tkinter import *
from PIL import ImageTk, Image
import pyglobe.pyglobe as map
import math
import itertools

class ImageZoomApp:
    def __init__(self, root):
        self.root = root
        self.root.title("pyglobe")
        self.root.geometry("800x600")

        self.mapWidth = 800
        self.mapHeight = 600

        self.TILE_SIZE = 256  # Define the size of each tile

        self.x = 0
        self.y = 0
        self.z = 0

        self.current_images = []

        # Create a Canvas widget
        self.canvas = Canvas(root, bg="gray75", height=self.mapHeight, width=self.mapWidth)
        self.canvas.pack(fill=BOTH, expand=True)
        root.update_idletasks()

        # Initialize image and image reference
        self.image = None
        self.tk_image = None

        # binding mouse wheel for zooming
        # TODO: properly support MacOs and unix systems <Button-4> and <Button-5> https://github.com/AndreasArendt/pyglobe/issues/1
        self.canvas.bind("<MouseWheel>", self.mapZoom)
        self.canvas.bind("<Button-1>", self.mapClick)
        self.setDefaultTile()

    def setDefaultTile(self):
        tile = map.getTileBytes(map.getTileUrl(x=0, y=0, z=0))
        self.updateMapTile(tile)

    def updateMapTile(self, tile, x=None, y=None):
        # Open the image file
        self.image = Image.open(tile)
        self.tk_image = ImageTk.PhotoImage(self.image)

        # Ensure canvas size is correct
        self.canvas.update_idletasks()  # Force canvas to update dimensions

        # If x or y is not provided, calculate center
        if x is None or y is None:
            x, y = self.mapWidth/2, self.mapHeight/2

        # Draw the image on the canvas, centered at (x, y)
        self.canvas.image = self.tk_image
        self.canvas.create_image(x, y, anchor=CENTER, image=self.tk_image)

        # Store the current image to avoid garbage collection
        self.current_images.append(self.tk_image)

    def getCanvasSize(self):
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width() * 2**self.z
        canvas_height = self.canvas.winfo_height() * 2**self.z

        return canvas_width, canvas_height

    def zoomCanvas(self, x, y, factor):
        bbox = self.canvas.bbox("all")
        self.canvas.scale("all", x, y, factor, factor)
        self.canvas.configure(scrollregion=bbox)
        self.canvas.update()
        self.canvas.update_idletasks()

    def mapClick(self, event):
        # Get canvas position of the mouse pointer
        self.canvas.update()

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        #tiles, xTile, yTile = self.getVisibleMapTiles(x,y)
        xTile, yTile = self.getTileIndices(x, y)

        print(f"Click coords: {x}, {y}")
        print(f"Tile indices: {xTile}, {yTile}")

    def getTileIndices(self, x, y):
        bbox = self.canvas.bbox("all")

        maxTiles = 2**self.z

        # limit x and y to map size, offset to 0,0
        deltaX = min(bbox[2], max(bbox[0], x)) - bbox[0]
        deltaY = min(bbox[3], max(bbox[1], y)) - bbox[1]

        xTile = min(max(0, round(deltaX / self.TILE_SIZE)), maxTiles-1)
        yTile = min(max(0, round(deltaY / self.TILE_SIZE)), maxTiles-1)

        assert(xTile >= 0 and xTile < maxTiles)
        assert(yTile >= 0 and yTile < maxTiles)

        return int(xTile), int(yTile)

    def getVisibleMapTiles(self, x, y):
        canvas_width, canvas_height = self.getCanvasSize()  # Get current canvas size
        bbox = self.canvas.bbox("all")

        width = canvas_width / 2**self.z - bbox[0]
        height = canvas_height / 2**self.z - bbox[1]

        maxTiles = 2**self.z  # Number of tiles in the current zoom level

        # Get current xy Tile
        xcoord = int(round((x / self.TILE_SIZE)))
        ycoord = int(round((y / self.TILE_SIZE)))

        xTile = min(xcoord, maxTiles-1)
        yTile = min(ycoord, maxTiles-1)

        xTile, yTile = self.getTileIndices(x, y)

        # Calculate delta to canvas border
        deltaLeft = (x - self.TILE_SIZE / 2) / self.TILE_SIZE
        deltaTop = (y - self.TILE_SIZE / 2) / self.TILE_SIZE
        deltaRight = (width - x - self.TILE_SIZE / 2) / self.TILE_SIZE
        deltaBottom = (height - y - self.TILE_SIZE / 2) / self.TILE_SIZE

        # Calculate how many tiles are visible on each side
        nTiles_left = math.ceil(deltaLeft)
        nTiles_top = math.ceil(deltaTop)
        nTiles_right = math.ceil(deltaRight)
        nTiles_bottom = math.ceil(deltaBottom)

        # Compute the range of visible tiles, ensuring bounds are within [0, maxTiles-1]
        minTileX = max(0, xTile - nTiles_left)
        maxTileX = min(maxTiles - 1, xTile + nTiles_right)
        minTileY = max(0, yTile - nTiles_top)
        maxTileY = min(maxTiles - 1, yTile + nTiles_bottom)

        # Generate visible tile indices
        xTiles = list(range(minTileX, maxTileX + 1))
        yTiles = list(range(minTileY, maxTileY + 1))

        # get permutation of all needed tiles and sort them by distance to current tile
        tilePermut = list(itertools.product(xTiles, yTiles))
        tiles_sorted = sorted(tilePermut, key=lambda tile: math.sqrt((tile[0] - xTile)**2 + (tile[1] - yTile)**2))

        return tiles_sorted, xTile, yTile

    def mapZoom(self, event=None):
        zoom_direction = int(event.delta / 120)  # Windows-specific behavior

        # Calculate scale factor based on zoom direction
        if self.z == 0 and zoom_direction < 0:
            factor = 1
        else:
            factor = 2 if zoom_direction > 0 else 0.5

        self.z += zoom_direction
        self.z = min(self.z, 19)
        self.z = max(self.z, 0)

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        self.zoomCanvas(x, y, factor)
        tiles, xTile, yTile = self.getVisibleMapTiles(x,y)

        print("numberTiles ", str(len(tiles)))
        self.current_images = []

        # redraw tiles
        for xyTile in tiles:
            url =  map.getTileUrl(x=xyTile[0], y=xyTile[1], z=self.z)
            tile = map.getTileBytes(url)

            offset_x = (xyTile[0] - xTile) * self.TILE_SIZE
            offset_y = (xyTile[1] - yTile) * self.TILE_SIZE

            self.updateMapTile(tile, x+offset_x, y+offset_y)

        # Pack or ensure canvas is displayed after drawing
        self.canvas.pack(fill=BOTH, expand=True)

        canvas_width = self.canvas.winfo_width() * 2**self.z
        canvas_height = self.canvas.winfo_height() *2**self.z

        # Debugging output
        print(f"Zoom coords: {x}, {y}")
        print(f"Zoom level: {self.z}")
        print(f"Tile indices: {xTile}, {yTile}")
        print(f"width: {canvas_width}, height: {canvas_height}")
        print("")

if __name__ == "__main__":
    root = Tk()
    app = ImageZoomApp(root)
    root.mainloop()
