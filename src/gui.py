import pyglobe.pyglobe as map
from tkinter import *
from PIL import ImageTk, Image
import tkinter as tk
from PIL import Image, ImageTk
import pyglobe.pyglobe as map

class ImageZoomApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Zoom")

        # Create a Canvas widget
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Initialize image and image reference
        self.image = None
        self.tk_image = None

        # Load an initial image (you can use your own image file)
        self.load_image()

        # binding mouse wheel for zooming
        # TODO: properly support MacOs and unix systems <Button-4> and <Button-5> https://github.com/AndreasArendt/pyglobe/issues/1
        self.canvas.bind("<MouseWheel>", self.mapZoom)

    def load_image(self):
        # Load the image using PIL (Python Imaging Library)
        # Get tile information
        x, y = map.wgs2tile(51, 0)
        tile_url = map.getTileUrl(x=x, y=y, z=8)
        tile_bytes = map.getTileBytes(tile_url)

        self.image = Image.open(tile_bytes)
        self.tk_image = ImageTk.PhotoImage(self.image)

        # Display the image on the Canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def mapZoom(self, event=None):
        print(event.delta)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageZoomApp(root)
    root.mainloop()
