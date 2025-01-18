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
        x, y = map.wgs2tile(51, 0)
        tileUrl = map.getTileUrl(x=x, y=y, z=8)
        return map.getTileBytes(tileUrl)

    def updateMapTile(self, tile):
        self.image = Image.open(tile)
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=NW, image=self.tk_image)

    def mapZoom(self, event=None):
        print(event.delta)

if __name__ == "__main__":
    root = Tk()
    app = ImageZoomApp(root)
    root.mainloop()
