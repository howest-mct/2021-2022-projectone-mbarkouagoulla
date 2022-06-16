from helpers.klasse_servo import SERVO
import time
servo_pin = 5

servo = SERVO(servo_pin)

while True:
    input('press to open')
    servo.open_deur()
    print('deur opent')
    # time.sleep(2)
    input('press to sluit')
    servo.sluit_deur()
    print('deur sluit')
    # time.sleep(2)
    


