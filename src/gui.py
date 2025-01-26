import pyglobe.pyglobe as map
from tkinter import *
from PIL import ImageTk, Image
import pyglobe.pyglobe as map

class ImageZoomApp:
    def __init__(self, root):
        self.root = root
        self.root.title("pyglobe")
        self.root.geometry("800x600")

        self.mapWidth = 800
        self.mapHeight = 600

        self.logical_width = 256
        self.logical_height = 256

        self.x = 0
        self.y = 0
        self.z = 0

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
            #w, h = self.getCanvasSize()
            #x, y = w / 2, h / 2
            x, y = self.mapWidth/2, self.mapHeight/2

        # Draw the image on the canvas, centered at (x, y)
        self.canvas.image = self.tk_image
        self.canvas.create_image(x, y, anchor=CENTER, image=self.tk_image)

        # Pack or ensure canvas is displayed after drawing
        self.canvas.pack(fill=BOTH, expand=True)

        # Store the current image to avoid garbage collection
        self.current_image = self.tk_image

    def getCanvasSize(self):
        canvas_width = self.canvas.winfo_width() * 2**self.z
        canvas_height = self.canvas.winfo_height() * 2**self.z

        return canvas_width, canvas_height

    def zoomCanvas(self, x, y, factor):
        self.canvas.scale("all", x, y, factor, factor)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def mapClick(self, event):
        # Get canvas position of the mouse pointer
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        print(f"Click coords: {x}, {y}")


    def mapZoom(self, event=None):
        zoom_direction = int(event.delta / 120)  # Windows-specific behavior
        self.z += zoom_direction
        self.z = min(self.z, 19)
        self.z = max(self.z, 0)

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        canvas_width, canvas_height = self.getCanvasSize()

        # Calculate scale factor based on zoom direction
        if self.z == 0 and zoom_direction < 0:
            factor = 1
        else:
            factor = 2 if zoom_direction > 0 else 0.5

        self.zoomCanvas(x, y, factor)

        maxTiles = 2**self.z
        xcoord = maxTiles * (x / canvas_width)
        ycoord = maxTiles * (y / canvas_height)

        xTile = int(xcoord)
        yTile = int(ycoord)

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        tileUrl = map.getTileUrl(x=xTile, y=yTile, z=self.z)
        self.updateMapTile(map.getTileBytes(tileUrl), x, y)

        # Debugging output
        print(tileUrl)
        print(f"Click coords: {x}, {y}")
        print(f"Zoom level: {self.z}")
        print(f"Canvas size pre-zoom: {canvas_width}, {canvas_height}")
        print(f"Normalized coords: {xcoord}, {ycoord}")
        print(f"Tile indices: {xTile}, {yTile}")
        print("")

if __name__ == "__main__":
    root = Tk()
    app = ImageZoomApp(root)
    root.mainloop()
