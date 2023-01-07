import time
import copy
import random
import tkinter

import numpy as np


from queue import Queue
from numba import jit, cuda
from threading import Thread
from PIL import Image, ImageTk, ImageGrab

#t[x][y] = (244, 244, 244)
#t2 = np.random.randint(0, 255, (x, y, 3))

# t = [
#         [
#             [72, 37],
#             [52, 14],
#             [35, 57],
#             [15, 15]
#         ],
#         [
#             [67, 47],
#             [87, 78],
#             [52, 21],
#             [23, 65]
#         ]
#     ]


class Scrumbler:
    @jit(target_backend='cuda', forceobj=True)
    def buildImage(self, image_copy_load, w, h):
        random_colors = np.random.randint(0, 255, (w, h, 3))

        print("Colors generated")

        for x_i, x in enumerate(random_colors):
            for y_i, y in enumerate(x):
                (r, g, b) = image_copy_load[(x_i, y_i)]
                image_copy_load[(x_i, y_i)] = (y[0] - r, y[1] - g, y[2] - b)

        print(f"Created image")
    
    def scrumbleImage(self, image, pixels, image_copy_load, image_copy, index, images):
        color_random1 = random.randrange(0, 255)
        color_random2 = random.randrange(0, 255)
        color_random3 = random.randrange(0, 255)

        if index <= 5:
            for i in range(image.size[0]):
                for j in range(image.size[1]):
                    (r, g, b) = pixels[(i, j)]
                    image_copy_load[(i, j)] = (
                        color_random1 - r,
                        color_random2 - g,
                        color_random3 - b,
                    )
        else:
            print(f"Building {index}")
            self.buildImage(image_copy_load, image.size[0], image.size[1])
            #random_reds = np.random.randint()

        print("Builded " + str(index))

        images.append(copy.copy(image_copy))

    def scrumbleScreen(self):
        image = ImageGrab.grab()
        pixels = image.load()
        image_copy = image.copy()
        image_copy_load = image_copy.load()

        images = []
        root = None
        lastRoot = None

        for xval in range(1, 11, 1):
            self.scrumbleImage(image, pixels, image_copy_load, image_copy, xval, images)

            if root:
                lastRoot = root

            root = tkinter.Toplevel()
            w = root.winfo_screenwidth()
            h = root.winfo_screenheight()
            root.state("zoomed")

            root.overrideredirect(1)
            root.geometry("%dx%d+0+0" % (w, h))
            root.focus_force()

            canvas = tkinter.Canvas(root, width=w, height=h)
            canvas.pack()

            (imgWidth, imgHeight) = image_copy.size

            if imgWidth > w or imgHeight > h:
                ratio = min(w / imgWidth, h / imgHeight)
                imgWidth = int(imgWidth * ratio)
                imgHeight = int(imgHeight * ratio)
                image_copy = image_copy.resize((imgWidth, imgHeight), Image.ANTIALIAS)

            image_m = ImageTk.PhotoImage(image_copy)
            imagesprite = canvas.create_image(w / 2, h / 2, image=image_m)

            root.update()

            if lastRoot:
                lastRoot.destroy()

            time.sleep(0.5)

        self.scrumbling = False

if __name__ == "__main__":
    Scrumbler().scrumbleScreen()