from RPi import GPIO
import time

class LCD:
    def __init__(self, lijstpinnen,rs_pin,e_pin):
        self.lijstpin = lijstpinnen
        self.rs = rs_pin
        self.e_pin = e_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(lijstpinnen, GPIO.OUT)
        GPIO.setup(rs_pin, GPIO.OUT)
        GPIO.setup(e_pin, GPIO.OUT)

    def __set_data_bits(self, value):
        mask = 0b00000001
        for index in range(0, 8):
            pin = self.lijstpin[index]
            if (value & mask) > 0:
                GPIO.output(pin, 1)
            else:
                GPIO.output(pin, 0)
            mask = mask << 1

    def send_instruction(self,value):
        GPIO.output(self.rs, 0)
        GPIO.output(self.e_pin, 1)
        self.__set_data_bits(value)
        GPIO.output(self.e_pin, 0)
        time.sleep(0.005)

    def send_character(self,value):
        GPIO.output(self.rs, 1)
        GPIO.output(self.e_pin, 1)
        self.__set_data_bits(value)
        GPIO.output(self.e_pin, 0)
        time.sleep(0.005)
    
    def write_message(self,value):
        i = 0
        for x in str(value):
            i += 1
            # print(x)
            if i == 17:
                # checken als de karakter op positie 17 zit
                self.send_instruction(0b10000000 | 0b01000000)
            self.send_character(ord(x))


    def init_LCD(self,cursorAan, cursorBlink):
        self.send_instruction(0x38)
        self.send_instruction(0b00001100 | (cursorAan << 1) | (cursorBlink << 0))
        self.send_instruction(1)
