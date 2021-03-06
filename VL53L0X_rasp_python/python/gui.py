import tkinter as tk
import picamera
import time
import math
import RPi.GPIO as GPIO
import pigpio
import threading
from time import sleep
import VL53L0X
    
# Initialize variables
camera = picamera.PiCamera()
top = tk.Tk()
pwmPinV = 12
pwmPinH = 19
solenoid = 15
GPIO.setmode(GPIO.BOARD)
GPIO.setup(solenoid, GPIO.OUT)
pi = pigpio.pi()

# LIDAR TOF sensor
tofMutex = threading.Lock()
tof = VL53L0X.VL53L0X()
tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

if not pi.connected:
    print("Error: Pi Not connected")
    exit()
    
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
# Column indices
DIST = 0
ANGLE = 1

# Control horizontal and vertical servos
def set_angle(angle, pwmPin):
    pi.set_servo_pulsewidth(pwmPin, 1000 + ((angle/180) * 1000)) 
    sleep(0.1)

# Sets GPIO outputs to power the solenoid
def fire():
    GPIO.output(solenoid, True)
    sleep(0.15)
    GPIO.output(solenoid, False)
    print("Firing")

# Opens the camera preview on the screen
#   Note: for VNC users to see the feed, the setting "Enable Direct Capture Mode" must be on
def start_camera():
    camera.preview_fullscreen=False
    camera.preview_window=(90,100, 1280, 720)
    camera.resolution=(1280,720)
    camera.start_preview()

# Callback function for the zoom scroll bar
def zoom(var):
    x = (100 - float(var))/100
    print(x)
    camera.zoom = (0,0,x,x) # (x, y, width, height)

# Set the angle of the horizontal servo
def horizontal_control(var):
    set_angle(int(var) + 105, pwmPinH)

# Set the angle of the vertical servo
def vertical_control(var):
    set_angle(int(var) + 90, pwmPinV)

# Measures distance to the target cup and sets the vertical servo angle appropriately
def aim():
    print("aiming")
    # Lower the vertical servo to aim the lidar sensor, get distance, and calculate angle
    vertical_control(10)
    sleep(1) # wait for the servo to rotate down
    # Get multiple distance measurements
    tofMutex.acquire()
    d1 = tof.get_distance()
    tofMutex.release()
    sleep(0.3)
    tofMutex.acquire()
    d2 = tof.get_distance()
    tofMutex.release()
    sleep(0.3)
    tofMutex.acquire()
    d3 = tof.get_distance()
    tofMutex.release()
    dist = (d1 + d2 + d3)/30
    print("Distance: " + str(dist) + " cm")
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
    print("distLo = " + str(distLo) + ", distHi = " + str(distHi))
    print("angleLo = " + str(angleLo) + ", angleHi = " + str(angleHi))
    # Interpolate the angle between them
    angle = angleHi - angleLo
    angle = angle * (dist - distLo) / (distHi - distLo)
    angle = math.ceil(angle + angleLo)
    print("Angle: " + str(angle))
    # Set the vertical position to the new angle
    vertical_control(angle)

# Closes relevant processes
def exit():
    top.destroy
    camera.stop_preview()
    camera.close()
    pi.set_servo_pulsewidth(pwmPinV, 0)
    pi.set_servo_pulsewidth(pwmPinH, 0)
    GPIO.cleanup()
    quit()

# GUI SETUP CODE 
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

# Updates the GUI text every second to display the LIDAR's distance measurement
def update_distance(name):
    while(1):
        tofMutex.acquire()
        distance = tof.get_distance()
        tofMutex.release()
        if (distance > 0):
            text.set("Distance: " + str(distance/10) + "cm")
        time.sleep(1)

def main():
    x = threading.Thread(target=update_distance, args=(1,))
    x.start()
    top.mainloop()

if __name__ == "__main__":
    main()
