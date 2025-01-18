import pyglobe.pyglobe as map
from tkinter import *
from PIL import ImageTk, Image
import pyglobe.pyglobe as map

class ImageZoomApp:
    def __init__(self, root):
        self.root = root
        self.root.title("pyglobe")

        # Create a Canvas widget
        self.canvas = Canvas(self.root, bg="white")
        self.canvas.pack(fill=BOTH, expand=True)

        # Initialize image and image reference
        self.image = None
        self.tk_image = None

        tile = self.getDefaultTile()
        self.updateMapTile(tile)

        # binding mouse wheel for zooming
        # TODO: properly support MacOs and unix systems <Button-4> and <Button-5> https://github.com/AndreasArendt/pyglobe/issues/1
        self.canvas.bind("<MouseWheel>", self.mapZoom)

    def getDefaultTile(self):
        # Get tile information
        self.x, self.y = map.wgs2tile(51, 0)
        self.z = 8
        tileUrl = map.getTileUrl(x=self.x, y=self.y, z=self.z)
        return map.getTileBytes(tileUrl)

    def updateMapTile(self, tile):
        self.image = Image.open(tile)
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=NW, image=self.tk_image)

    def mapZoom(self, event=None):
        self.z += event.delta / 120 # windows specific
        self.z = min(self.z, 19)
        self.z = max(self.z, 0)

        tileUrl = map.getTileUrl(x=self.x, y=self.y, z=self.z)
        self.updateMapTile(map.getTileBytes(tileUrl))

if __name__ == "__main__":
    root = Tk()
    app = ImageZoomApp(root)
    root.mainloop()
