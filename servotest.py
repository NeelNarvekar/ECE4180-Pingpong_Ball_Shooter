import RPi.GPIO as GPIO
from time import sleep

pwmPin = 13

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pwmPin, GPIO.OUT)

def setAngle(angle):
    duty = angle / 18 + 3
    GPIO.output(pwmPin, True)
    pwm.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(pwmPin, False)
    pwm.ChangeDutyCycle(duty)


pwm=GPIO.PWM(pwmPin, 50)
pwm.start(0)

for i in range(3):
    for i in range(5):
        print("Servo " + str(45*i))
        setAngle(45*i) # left -90 deg position
        sleep(0.1)

pwm.stop()
GPIO.cleanup()
