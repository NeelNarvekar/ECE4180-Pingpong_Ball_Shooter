#!/usr/bin/python

#text window to show distance on time of flight sensor in cm
# or button to update distance
# 4 sliders to test how zoom works

import tkinter as tk
import picamera
import time
import RPi.GPIO as GPIO
from time import sleep
import VL53L0X
import threading

tof = VL53L0X.VL53L0X()
tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

timing = tof.get_timing()
if (timing < 20000):
   timing = 20000
    
camera = picamera.PiCamera()
top = tk.Tk()
pwmPin1 = 13
pwmPin2 = 11
solenoid = 15
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pwmPin1, GPIO.OUT)
GPIO.setup(pwmPin2, GPIO.OUT)
GPIO.setup(solenoid, GPIO.OUT)
pwm1=GPIO.PWM(pwmPin1, 50)
pwm2=GPIO.PWM(pwmPin2, 50)
pwm1.start(0)
pwm2.start(0)

# Mapping between distance measured and vertical angle
# Column 0 = Distance, Column 1 = Mapping
#              cm  degrees
aim_mapping = [[0,    143],
               [6.3,  140],
               [18,   135],
               [21.2, 130],
               [34.4, 125],
               [44,   120],
               [54,   110],
               [60,   100],
               [65,    90],
               [70,    80],
               [1000,  75]]
DIST = 0
ANGLE = 1


def set_angle(angle, pwmPin, pwm):
    print("setting angle")
    duty = angle / 18 + 3
    GPIO.output(pwmPin, True)
    pwm.ChangeDutyCycle(duty)
#     sleep(1)
    GPIO.output(pwmPin, False)
    pwm.ChangeDutyCycle(duty)
    
def fire():
    GPIO.output(solenoid, True)
    sleep(0.5)
    GPIO.output(solenoid, False)
    print("Firing")
    
    for count in range(1,101):
        distance = tof.get_distance()
        if (distance > 0):
            print ("%d mm, %d cm, %d" % (distance, (distance/10), count))

        time.sleep(timing/1000000.00)

    tof.stop_ranging()

def start_camera():
    camera.preview_fullscreen=False
    camera.preview_window=(90,100, 320, 240)
    camera.resolution=(640,480)
    camera.start_preview()

def zoom(var):
    x = (109 - float(var))/100
    camera.zoom = (0.5,0.5,x,x)

def horizontal_control(var):
    set_angle(int(var), pwmPin1, pwm1)

def vertical_control(var):
    set_angle(int(var), pwmPin2, pwm2)
    #print(int(var))

def aim():
    print("aiming")
    # Lower the vertical servo to aim the lidar sensor, get distance, and calculate angle
    vertical_control(10)
    sleep(0.8) # wait for the servo to rotate down
    dist = tof.get_distance()
    # Map the distance to the proper angle
    distLo = aim_mapping[0][DIST]
    distHi = aim_mapping[1][DIST] 
    angleLo = aim_mapping[0][ANGLE]
    angleHi = aim_mapping[1][ANGLE]
    # Find the two distances points around this distance
    idxLo = 0
    while (dist > distHi):
        idxLo += 1
        distLo = aim_mapping[idxLo][DIST]
        distHi = aim_mapping[idxLo+1][DIST]
    angleLo = aim_mapping[idxLo][ANGLE]
    angleHi = aim_mapping[idxLo+1][ANGLE]
    # Interpolate the angle between them
    angle = angleHi - angleLo
    angle = angle * (dist - distLo) / (distHi - distLo)
    angle = angle + angleLo
    # Set the vertical position to the new angle
    vertical_control(angle)
        

def exit():
    top.destroy
    camera.stop_preview()
    camera.close()
    pwm.stop()
    GPIO.cleanup()
    quit()

# GUI SETUP CODE #
top.resizable(width=False, height=False)
top.geometry("600x200")

buttonframe = tk.Frame(top, width=500, height=500)
buttonframe.grid(row=3, column=6, sticky="nesw")

text = tk.StringVar()
text.set("Distance: ")
label = tk.Label(buttonframe, textvariable=text).grid(row=1, column=1, columnspan=4)

tk.Button(buttonframe, text="Start Camera", command=start_camera).grid(row=3, column=1)
tk.Button(buttonframe, text = "Aim", command=aim).grid(row=3, column=2)
tk.Button(buttonframe, text="Fire!", command=fire).grid(row=3, column=3)
tk.Button(buttonframe, text="Exit", command=exit).grid(row=3, column=4)

tk.Scale(buttonframe, from_=0, to=180, orient=tk.HORIZONTAL, label = "Horizontal", command=horizontal_control, length=150).grid(row=2, column=1, columnspan=4)
tk.Scale(buttonframe, from_=180, to=0, orient=tk.VERTICAL, label = "Vertical", command=vertical_control, length=150).grid(row=1, column=5, rowspan=3)
tk.Scale(buttonframe, from_=99, to=10, orient=tk.VERTICAL, label = "Zoom", command=zoom, length=150).grid(row=1,column=6, rowspan=3)

buttonframe.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

def update_distance(name):
    while(1):
        distance = tof.get_distance()
        if (distance > 0):
            text.set("Distance: " + str(distance/10) + "cm")
        time.sleep(1)

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

def main():
    x = threading.Thread(target=update_distance, args=(1,))
    x.start()
    top.mainloop()

if __name__ == "__main__":
    main()
