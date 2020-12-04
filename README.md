# ECE4180-Pingpong_Ball_Shooter

Georgia Tech ECE 4180: Embedded Systems Design
Final Project

Ping Pong Ball Shooter 

By:
Neel Narvekar
Connor Truono
Tony Wineman

For detailed documentation, see the Wiki page at:
https://github.com/NeelNarvekar/ECE4180-Pingpong_Ball_Shooter/wiki/ECE4180-Pingpong_Ball_Shooter

## Important usage note: 
The gui.py in the top directory is NOT the working file. There are issues with importing and linking library in other folders. The proper file is VL53L0X_rasp_python/python/gui.py

# From the Wiki:

## Parts List:
1. Robotic arm kit (1)
2. Servo Motors (2)
3. 12V Solenoid (1)
4. VL53L0X LiDAR (1)
5. Raspberry Pi 4 (1)
6. Pi camera (1)
7. Ping pong ball(s)
8. 5V Relay (1)
9. 12V Power supply (1)
10. Breadboard (1)
11. Jumper wires

## Project Description:
The goal of this project is to create a ping pong ball cannon that can automatically aim itself to hit any cup. Perfect for any college party!

We accomplished this by putting our _Embedded Systems Design_ skills to good use, using a Raspberry Pi to control an array of peripheral hardware to accomplish this goal in a user-friendly fashion! In addition, we explored the use of CAD models and 3D printing and to create a proper barrel.

All of our code was written in Python and can be found in this GitHub repo: https://github.com/NeelNarvekar/ECE4180-Pingpong_Ball_Shooter.
The external library _VL53L0X Python interface on Raspberry Pi_ by _cassou_ was used to interact with the LIDAR TOF sensor.

## Setup

1. Install required libraries
- Tkinter: `sudo apt-get install python-tk`
- Picamera: `sudo apt-get install python-picamera python3-picamera`
- RPi.GPIO: `pip install RPi.GPIO`
- Pigpio (should be preinstalled)

2. Enable required interfaces
- run `sudo raspi-config`
- Under the interfaces section, enable I2C and the Camera

3. Run the program
- run `python3 VL53L0X_rasp_python/python/gui.py`
- NOTE: The gui.py at the highest level directory is not linked with the library so it will not run. Gui.py must be run from the location listed above.

## Hardware Setup
There were a couple of things we did with the hardware while we were setting up our system.
* We offset the ping pong ball in the barrel to ensure that the solenoid hit the ball at the very end of it's extension. This increased the range of our launcher.
* We utilized a 3D printer to create the barrel for our ping pong ball shooter.
* To get 2 degrees of freedom with our launcher we used the robotic arm kit which allows two servos to be mounted to each other. This was then secured to a wooden base for stability.

## Schematic:
![129342160_435260504147839_5452285941601668298_n](https://user-images.githubusercontent.com/33188523/101075585-395df400-3570-11eb-94b6-33d03a1925bc.jpg)

This schematic shows the wiring connections between the pi and all peripherals. It also details the exact pins that were used on the Raspberry Pi.

## Photos:
![129014430_439958903665409_4076589644453647088_n](https://user-images.githubusercontent.com/33188523/101075590-3b27b780-3570-11eb-9817-5c5d190d64f3.jpg)
![128896108_661722777858298_1531081347986068901_n](https://user-images.githubusercontent.com/33188523/101106832-f9facc00-359e-11eb-9ff3-1a027ec10d83.jpg)

Hardware setup of our ping pong ball shooter. All of the hardware is mounted to a wooden board for stability, and the Pi's power comes from a USB-C power connector.

<img width="552" alt="Screen Shot 2020-12-03 at 11 24 29 AM" src="https://user-images.githubusercontent.com/33188523/101077788-4fb97f00-3573-11eb-845b-aa438487e598.png">

3D printed barrel to stabilize the ping pong ball for consistent launches.

## Source Code Walkthrough:

This section will step through most of the source code in the main Python file, gui.py. 

For a full view of the source code, [see its repo page](https://github.com/NeelNarvekar/ECE4180-Pingpong_Ball_Shooter/blob/main/gui.py).

### Imported Libraries
Most of these are self-explanatory are are used for interacting with external hardware. A couple exceptions are as follows: 
 - tkinter, an API for GUI's in Python
 - VL53L0X, the Python file which exposes C functions buried in this library's folders
```Python
import tkinter as tk
import picamera
import time
import math
import RPi.GPIO as GPIO
import pigpio
import threading
from time import sleep
from VL53L0X_rasp_python.python import VL53L0X
```

### Setup and variable initialization
When declaring GPIO pins, note that the solenoid's pin number 15 corresponds to the physical pin number on the Pi's hardware interface (counting in order from 1-40), where the servos' numbers (12 and 19) correspond to actual the GPIO pin, listed out of order. This is confusing to write about, but see the diagram at this page to learn the difference between the numbering: https://www.raspberrypi.org/documentation/usage/gpio/

```Python
camera = picamera.PiCamera()
top = tk.Tk()
pwmPinV = 12
pwmPinH = 19
solenoid = 15
GPIO.setmode(GPIO.BOARD)
GPIO.setup(solenoid, GPIO.OUT)
pi = pigpio.pi()
```

A Mutex lock is initialized with the LIDAR sensor, since it will be used both in the aim button's callback function and in a separate thread that periodically updates the GUI. 
```Python
tofMutex = threading.Lock()
tof = VL53L0X.VL53L0X()
tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
```

To determine the optimal launch angle for any distance, we took a series of measurements spanning the whole range of the cannon (~75 cm) to find the optimal launch angle at each difference. This data and a rough graph and trending curve can be seen here:
![129631702_835318287261823_9081453109402454082_n](https://user-images.githubusercontent.com/33188523/101092289-6f5aa280-3587-11eb-9b47-a5a3f0d795c7.png)
The aim function will interpolate a proper angle for any distance between these data points. The index variables _DIST_ and _ANGLE_ are used to 2D array navigation more clear. 
(Note: the maximum measurement from the TOF sensor is around 810 cm, so the last mapping of 1000 cm and 75 degrees takes into account any measurement that is out of range.)
```Python
DIST = 0
ANGLE = 1
#              cm  degrees
aim_mapping = [[0,   143],
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
```

### Creating the GUI
Jumping over the function definitions for the time being, the next logical step in this program is initializing the GUI from Tkinter. The following code will create a new window (_top_) and add four buttons and three selector scroll bars.
```Python
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
```

### GUI Function Definitions
Now let's go through what each of those buttons and control bars do! All of these functions are called upon interacting with the GUI.

These first functions _start\_camera_ and _zoom_ control the Pi camera. 
```Python
def start_camera():
    camera.preview_fullscreen=False
    camera.preview_window=(90,100, 1280, 720)
    camera.resolution=(1280,720)
    camera.start_preview()

def zoom(var):
    x = (100 - float(var))/100
    print(x)
    camera.zoom = (0,0,x,x) # (x, y, width, height)
```

The user can manually control the servo using the horizontal and vertical selection bars with _horizontal\_control_ and _vertical\_control_, which both call _set\_angle_ to interact with the PWM pins.
```Python
def set_angle(angle, pwmPin):
    pi.set_servo_pulsewidth(pwmPin, 1000 + ((angle/180) * 1000)) 
    sleep(0.1)

def horizontal_control(var):
    set_angle(int(var) + 105, pwmPinH)

def vertical_control(var):
    set_angle(int(var) + 90, pwmPinV)
```

Enough setup. Let's hit some targets! 
The aim function brings everything together. This assumes the user has horizontally aligned the cannon for the proper cup. It will set the vertical angle to 10 degrees to measure the distance to whatever target you have selected (measurement above camera-level allows the user to select any target, even behind an obstacle!). 
After measuring the distance, it will calculate the proper launch angle using the data from the _aim\_mapping_ matrix using linear interpolation between data ponts. It then sets the servo's vertical position to that angle, and it's ready to fire.
```Python
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
```

Now to fire the cannon! This simple functions sets the relay's GPIO pin high to close the switch on the 12V power supply for a short time to hit the ping pong ball, then releases it. 
```Python
def fire():
    print("Firing")
    GPIO.output(solenoid, True)
    sleep(0.15)
    GPIO.output(solenoid, False)
```

This _update\_distance_ function will read in the current distance from the LIDAR sensor from the VL53L0X and update the GUI's text once every second. Don't forget your mutex!
```Python
def update_distance(name):
    while(1):
        tofMutex.acquire()
        distance = tof.get_distance()
        tofMutex.release()
        if (distance > 0):
            text.set("Distance: " + str(distance/10) + "cm")
        time.sleep(1)
```

Finally, the _exit_ function does exactly what you expect: closes down all the necessary processes and quits execution.
```Python
def exit():
    top.destroy
    camera.stop_preview()
    camera.close()
    pi.set_servo_pulsewidth(pwmPinV, 0)
    pi.set_servo_pulsewidth(pwmPinH, 0)
    GPIO.cleanup()
    quit()
```

### Start it up!
The last bit of uncovered code calls the proper functions to get things started. _Main_ gets the distance thread running and sets the GUI in motion.  
```Python
def main():
    x = threading.Thread(target=update_distance, args=(1,))
    x.start()
    top.mainloop()

if __name__ == "__main__":
    main()
```

And that's how our software works!

## Videos:
### [---Demo---](https://www.youtube.com/watch?v=OaZST7tzSOE&feature=youtu.be&fbclid=IwAR1YTzGc3ulHCY9Nk1NFiXgEzEhbsBmEkhhNBPb2QPzUoJQ5R7T1DriIDhk)
### [---Presentation---](https://www.youtube.com/watch?v=-Ud2g-wNmS4&feature=youtu.be&fbclid=IwAR3kU-L6J-VJdtrgU7dnOb62WwOcdmjlQD1fOdErlFZv_T5lCBokvsg3UWM)

## Future Improvements:
There are various ways that this project could be improved for future iterations:

### Solenoid Cannon
While our solenoid was the largest the lab could offer, it did not provide the power to achieve the desired ping pong ball range. The issue was not that it could not push the ping pong ball properly, of course. Those things are light! However, the speed at impact was the limiting factor on how fast the ping pong ball could be struck. A solenoid with higher force rating and a lighter core (Acceleration = Force / Mass) would be more useful for striking the ball at higher ranges.

### Power Supply Convenience
A future iteration could make the design more compact and portable by replacing the usage of multiple power supplies (USB-C connector to the Pi + 12V external supply for the solenoid) with a single power supply (or 12V battery) with a voltage regulator to power both devices.

### Camera Feed Display
From all of our research, it does not seem like there is a way to add text or images on top of the Raspberry Pi camera's preview feed (though that seems like a really interesting project now!). However, if a future iteration of this project used a different video streaming platform, it would be useful to add a crosshair in the middle of the camera's feed to improve horizontal aiming.

### Target Detection and Selection for Automatic Horizontal Aiming
If only we had time to learn and implement a computer vision algorithm. Oh well. This feature idea would involve the program analyzing the camera's feed to detect cups, expose an interface for the user to select their target cup, and automatically aim the horizontal servo to target that cup. 

### 2D Aiming
Our aiming function is currently limited to targets that are on a similar plane to the ball cannon. Future iterations could allow a second dimension of targeting and aiming in hitting targets at a higher and lower elevation. However, for our data-and-interpolation-based approach of finding the proper angles to hit targets at different distances, adding a second dimension of aiming added unnecessary tedium that would not have fit within time constraints.
