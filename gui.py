#!/usr/bin/python

import tkinter as tk
import picamera
import time
import RPi.GPIO as GPIO
from time import sleep
import VL53L0X

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
    print(int(var))

def exit():
    top.destroy
    camera.stop_preview()
    camera.close()
    pwm.stop()
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

    tk.Scale(buttonframe, from_=0, to=180, orient=tk.HORIZONTAL, label = "Horizontal", command=horizontal_control, length=150).grid(row=1, column=1, columnspan=3)
    tk.Scale(buttonframe, from_=180, to=0, orient=tk.VERTICAL, label = "Vertical", command=vertical_control, length=150).grid(row=1, column=4, rowspan=2)
    tk.Scale(buttonframe, from_=99, to=10, orient=tk.VERTICAL, label = "Zoom", command=zoom, length=150).grid(row=1,column=5, rowspan=2)

    buttonframe.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    top.mainloop()

def main():
    setup_gui()

if __name__ == "__main__":
    main()
