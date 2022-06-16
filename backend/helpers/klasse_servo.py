from RPi import GPIO
import time


class SERVO:
    def __init__(self, servo_pin):
        self.servo_pin = servo_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.servo_pin, GPIO.OUT)
        self.pwm= GPIO.PWM(self.servo_pin, 50)
        self.pwm.start(0)
        # servo = GPIO.PWM(servo_pin, 50)
        # servo.start(7.5)  
        # servo.ChangeDutyCycle(12)  # 3 is 0 graden, 12 is 180 graden

    
    def open_deur(self):
        self.pwm.ChangeDutyCycle(1.6)
        time.sleep(.5)
        self.pwm.ChangeDutyCycle(0)

    def sluit_deur(self):
        self.pwm.ChangeDutyCycle(5.6)
        time.sleep(.5)
        self.pwm.ChangeDutyCycle(0)
        