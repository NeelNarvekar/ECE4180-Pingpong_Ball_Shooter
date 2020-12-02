#!/usr/bin/python

import tkinter as tk
import picamera
import time
import RPi.GPIO as GPIO
import pigpio
import threading
from time import sleep
import VL53L0X
    
camera = picamera.PiCamera()
top = tk.Tk()
pwmPinV = 12
pwmPinH = 19
solenoid = 15
GPIO.setmode(GPIO.BOARD)
#GPIO.setup(pwmPin1, GPIO.OUT)
#GPIO.setup(pwmPin2, GPIO.OUT)
GPIO.setup(solenoid, GPIO.OUT)
#pwmH=GPIO.PWM(pwmPin1, 50)
#pwmV=GPIO.PWM(pwmPin2, 50)
#pwmV.start(0)
pi = pigpio.pi()

tof = VL53L0X.VL53L0X()
tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

if not pi.connected:
    exit()
    
# Mapping between distance measured and vertical angle
# Column 0 = Distance, Column 1 = Mapping
#              cm  degrees
aim_mapping = [0,    143,
               6.3,  140,
               18,   135,
               21.2, 130,
               34.4, 125,
               44,   120,
               54,   110,
               60,   100,
               65,    90,
               70,    80,
               1000,  75]
DIST = 0
ANGLE = 1


def set_angle(angle, pwmPin):
    #print("setting angle")
    pi.set_servo_pulsewidth(pwmPin, 1000 + ((angle/180) * 1000)) 
    sleep(0.1)

    
def fire():
    GPIO.output(solenoid, True)
    sleep(0.15)
    GPIO.output(solenoid, False)
    print("Firing")
#     tof = VL53L0X.VL53L0X()
#     tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
#     
#     timing = tof.get_timing()
#     if (timing < 20000):
#         timing = 20000
#     
#     for count in range(1,101):
#         distance = tof.get_distance()
#         if (distance > 0):
#             print ("%d mm, %d cm, %d" % (distance, (distance/10), count))
# 
#         time.sleep(timing/1000000.00)
# 
#     tof.stop_ranging()

def start_camera():
    camera.preview_fullscreen=False
    camera.preview_window=(90,100, 1280, 720)
    camera.resolution=(1280,720)
    camera.start_preview()

def zoom(var):
    x = (100 - float(var))/100
    print(x)
    camera.zoom = (0,0,x,x) # (x, y, width, height)

def horizontal_control(var):
    set_angle(int(var) + 105, pwmPinH)

def vertical_control(var):
    set_angle(int(var) + 90, pwmPinV)
    print(int(var))

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
    pi.set_servo_pulsewidth(pwmPinV, 0)
    pi.set_servo_pulsewidth(pwmPinH, 0)
    GPIO.cleanup()
    quit()

# GUI SETUP CODE #
top.resizable(width=False, height=False)
top.geometry("600x300")

buttonframe = tk.Frame(top, width=500, height=500)
buttonframe.grid(row=3, column=6, sticky="nesw")

text = tk.StringVar()
text.set("Distance: ")
label = tk.Label(buttonframe, textvariable=text).grid(row=1, column=1, columnspan=4)

tk.Button(buttonframe, text="Start Camera", command=start_camera).grid(row=3, column=1)
tk.Button(buttonframe, text = "Aim", command=aim).grid(row=3, column=2)
tk.Button(buttonframe, text="Fire!", command=fire).grid(row=3, column=3)
tk.Button(buttonframe, text="Exit", command=exit).grid(row=3, column=4)

tk.Scale(buttonframe, from_=-60, to=60, orient=tk.HORIZONTAL, label = "Horizontal", command=horizontal_control, length=200).grid(row=2, column=1, columnspan=4)
tk.Scale(buttonframe, from_=145, to=-45, orient=tk.VERTICAL, label = "Vertical", command=vertical_control, length=280).grid(row=1, column=5, rowspan=3)
tk.Scale(buttonframe, from_=99, to=0, orient=tk.VERTICAL, label = "Zoom", command=zoom, length=280).grid(row=1,column=6, rowspan=3)

buttonframe.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

def update_distance(name):
    while(1):
        distance = tof.get_distance()
        if (distance > 0):
            text.set("Distance: " + str(distance/10) + "cm")
        time.sleep(1)

def main():
    x = threading.Thread(target=update_distance, args=(1,))
    x.start()
    top.mainloop()

if __name__ == "__main__":
    main()
