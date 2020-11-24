#!/usr/bin/python

import tkinter as tk
import picamera
import time
import RPi.GPIO as GPIO
import pigpio
from time import sleep
#import VL53L0X
    
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

if not pi.connected:
    exit()
    


def set_angle(angle, pwmPin):
    #print("setting angle")
    pi.set_servo_pulsewidth(pwmPin, 1000 + ((angle/180) * 1000)) 
    sleep(0.1)

    
def fire():
    GPIO.output(solenoid, True)
    sleep(0.5)
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

def exit():
    top.destroy
    camera.stop_preview()
    camera.close()
    pi.set_servo_pulsewidth(pwmPinV, 0)
    pi.set_servo_pulsewidth(pwmPinH, 0)
    GPIO.cleanup()
    quit()

def setup_gui():
    top.resizable(width=False, height=False)
    top.geometry("500x200")

    buttonframe = tk.Frame(top, width=500, height=500)
    buttonframe.grid(row=2, column=5, sticky="nesw")

    tk.Button(buttonframe, text="Fire!", command=fire).grid(row=2, column=1)
    tk.Button(buttonframe, text="Start Camera", command=start_camera).grid(row=2, column=2)
    tk.Button(buttonframe, text="Exit", command=exit).grid(row=2, column=3)

    tk.Scale(buttonframe, from_=-60, to=60, orient=tk.HORIZONTAL, label = "Horizontal", command=horizontal_control, length=150).grid(row=1, column=1, columnspan=3)
    tk.Scale(buttonframe, from_=120, to=0, orient=tk.VERTICAL, label = "Vertical", command=vertical_control, length=150).grid(row=1, column=4, rowspan=2)
    tk.Scale(buttonframe, from_=99, to=0, orient=tk.VERTICAL, label = "Zoom", command=zoom, length=150).grid(row=1,column=5, rowspan=2)

    buttonframe.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    top.mainloop()

def main():
    setup_gui()

if __name__ == "__main__":
    main()
