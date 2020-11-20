#!/usr/bin/python

import tkinter as tk
# import RPi.GPIO as GPIO
# import picamera

def fire():
	print("Firing")

def start_camera():
    camera.preview_fullscreen=False
    camera.preview_window=(90,100, 320, 240)
    camera.resolution=(640,480)
    camera.start_preview()

def Zoom(var):
    x = float("0."+var)
    print(x)
    # camera.zoom = (0.5,0.5,x,x)

def exit():
    top.destroy
    # camera.stop_preview()
    # camera.close()
    quit()

top = tk.Tk()
top.resizable(width=False, height=False)
top.geometry("500x200")

buttonframe = tk.Frame(top, width=500, height=200)
buttonframe.grid(row=2, column=4, sticky="nesw")

value = tk.DoubleVar()

scale = tk.Scale(buttonframe, orient=tk.HORIZONTAL, variable=value, from_=0, to=180, length=300)
scale.grid(row=1, column=1, columnspan=3)

tk.Button(buttonframe, text="Fire!", command=fire).grid(row=2, column=1)
tk.Button(buttonframe, text="Start Camera", command=start_camera).grid(row=2, column=2)
tk.Button(buttonframe, text="Exit", command=exit).grid(row=2, column=3)

tk.Scale(buttonframe, from_=99, to=10, orient=tk.VERTICAL, label = "Zoom", command=Zoom).grid(row=1,column=4, rowspan=2)

# button.pack(anchor=tk.CENTER)

# buttonframe.pack(fill="both", expand=True, padx=20, pady=20)
buttonframe.place(relx=0.5, rely=0.5, anchor=tk.CENTER)


top.mainloop()