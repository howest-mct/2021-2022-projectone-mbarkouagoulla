import RPi.GPIO as GPIO
import time
from helpers.klasse_servo import SERVO
GPIO.setmode(GPIO.BCM)
poweroff = 6
GPIO.setup(poweroff, GPIO.IN, pull_up_down=GPIO.PUD_UP)
servo= SERVO(5)

while True:
    servo.open_deur()
    print('open')
    time.sleep(1)
    servo.sluit_deur()
    print('sluit')
    time.sleep(1)
    # button_waarde = GPIO.input(poweroff)
    # print(f'poweroff>{button_waarde}')


