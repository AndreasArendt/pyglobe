import pyglobe.pyglobe as map

from tkinter import *
from PIL import ImageTk, Image

root = Tk()
root.title("Map")

x, y = map.wgs2tile(51,0)
tileUrl = map.getTileUrl(x=x, y=y, z=8)
tileBytes = map.getTileBytes(tileUrl)

class WebImage:
    def __init__(self, url):
        try:
            self.image = ImageTk.PhotoImage(Image.open(tileBytes))
        except Exception as e:
            print(f"Error loading image from {url}: {e}")
            self.image = None  # Fallback to None if loading fails

    def get(self):
        return self.image

# Fetch and display the map tile
img = WebImage(tileUrl).get()
if img:
    imagelab = Label(root, image=img)
    imagelab.grid(row=0, column=0)
else:
    print("Image could not be loaded. Check the URL or internet connection.")

root.mainloop()
