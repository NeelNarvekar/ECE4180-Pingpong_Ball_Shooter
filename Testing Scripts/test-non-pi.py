#!/usr/bin/python

import tkinter as tk
import time
from time import sleep

top = tk.Tk()
angleV = 0.0
angleH = 0.0

def set_angle(angle, pwmPin, pwm):
    print("setting angle")
    duty = angle / 18 + 3
    GPIO.output(pwmPin, True)
    pwm.ChangeDutyCycle(duty)
#     sleep(1)
    GPIO.output(pwmPin, False)
    pwm.ChangeDutyCycle(duty)
    
def fire():
    print("Firing")


def horizontal_control(var):
    angleH = var

def vertical_control(var):
    angleV = var

def exit():
    top.destroy
    quit()

def setup_gui():
    top.resizable(width=False, height=False)
    top.geometry("500x200")

    buttonframe = tk.Frame(top, width=500, height=500)
    buttonframe.grid(row=2, column=5, sticky="nesw")

    tk.Button(buttonframe, text="Fire!", command=fire).grid(row=2, column=1)
#    tk.Button(buttonframe, text="Start Camera", command=start_camera).grid(row=2, column=2)
    tk.Button(buttonframe, text="Exit", command=exit).grid(row=2, column=3)

    tk.Scale(buttonframe, from_=0, to=180, orient=tk.HORIZONTAL, label = "Horizontal", command=horizontal_control, length=150).grid(row=1, column=1, columnspan=3)
    tk.Scale(buttonframe, from_=180, to=0, orient=tk.VERTICAL, label = "Vertical", command=vertical_control, length=150).grid(row=1, column=4, rowspan=2)
#    tk.Scale(buttonframe, from_=99, to=10, orient=tk.VERTICAL, label = "Zoom", command=zoom, length=150).grid(row=1,column=5, rowspan=2)

    #text_angleH = tk.Label(top, text = "Horizontal: " + str(angleH))
    #text_angleH.place(x=20, y=10)

    buttonframe.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    top.mainloop()

# Kinematics Functions (using units of meters/second)

def findHorizontalDistance(v, theta, dy):
    vx = v*cos(theta)
    vy = v*sin(theta)
    t = (vy + sqrt(vy*vy+19.6*dy))/9.8
    xf = vx * t
    return xf

def sweepAndFindOptimalAngle(v, dx, dy):
    bestAngle = 0
    bestDist = abs(findHorizontalDistance(v, bestAngle, dy) - dx)
    for curAngle in range(61):
        curDist = abs(findHorizontalDistance(v, curAngle, dy) - dx)
        if (curDist < bestDist):
            bestAngle = curAngle
            bestDist = curDist
    return bestAngle
        

#def findOptimalAngle(v, dx, dy):
#    # Search through a space of different angles to find how to shoot
#    lowAngle = 0
#    midAngle = 30
#    hiAngle = 60
#    lowDist = findHorizontalDistance(v, lowAngle, dy)
#    midDist = findHorizontalDistance(v, midAngle, dy)
#    hiDist = findHorizontalDistance(v, hiAngle, dy)
#    while True:
#        # See if the desired distance is between some of these
#        lowDist = findHorizontalDistance(v, lowAngle, dy)
#        midDist = findHorizontalDistance(v, midAngle, dy)
#        hiDist = findHorizontalDistance(v, hiAngle, dy)
#        # C
#        dist = findHorizontalDistance(v, theta, dy)
#        if (abs(midDist - dx) < 0.05):
#            break
        

def main():
    setup_gui()

if __name__ == "__main__":
    main()
