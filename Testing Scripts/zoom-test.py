#!/usr/bin/python

import tkinter as tk
import time
import picamera
from time import sleep
    
camera = picamera.PiCamera()
top = tk.Tk()

camera.preview_fullscreen=False
camera.preview_window=(90,100, 1280, 720)
camera.resolution=(1280,720)
camera.start_preview()

def zoom1(var):
    x = (100 - float(var))/100
    print(x)
    camera.zoom = (x,camera.zoom[1],camera.zoom[2],camera.zoom[3]) # (x, y, width, height)

def zoom2(var):
    x = (100 - float(var))/100
    print(x)
    camera.zoom = (camera.zoom[0],x,camera.zoom[2],camera.zoom[3]) # (x, y, width, height)

def zoom3(var):
    x = (100 - float(var))/100
    print(x)
    camera.zoom = (camera.zoom[0],camera.zoom[1],x,camera.zoom[3]) # (x, y, width, height)

def zoom4(var):
    x = (100 - float(var))/100
    print(x)
    camera.zoom = (camera.zoom[0],camera.zoom[1],camera.zoom[2],x) # (x, y, width, height)

def exit():
    top.destroy
    camera.stop_preview()
    camera.close()
    quit()
    

# GUI SETUP CODE #
top.resizable(width=False, height=False)
top.geometry("600x200")

buttonframe = tk.Frame(top, width=500, height=500)
buttonframe.grid(row=1, column=4, sticky="nesw")

tk.Scale(buttonframe, from_=99, to=0, orient=tk.VERTICAL, label = "Zoom", command=zoom1, length=150).grid(row=1,column=1)
tk.Scale(buttonframe, from_=99, to=0, orient=tk.VERTICAL, label = "Zoom", command=zoom2, length=150).grid(row=1,column=2)
tk.Scale(buttonframe, from_=99, to=0, orient=tk.VERTICAL, label = "Zoom", command=zoom3, length=150).grid(row=1,column=3)
tk.Scale(buttonframe, from_=99, to=0, orient=tk.VERTICAL, label = "Zoom", command=zoom4, length=150).grid(row=1,column=4)

tk.Button(buttonframe, text="Exit", command=exit).grid(row=1, column=5)


buttonframe.place(relx=0.5, rely=0.5, anchor=tk.CENTER)


def main():
    top.mainloop()

if __name__ == "__main__":
    main()
