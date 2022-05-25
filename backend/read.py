import multiprocessing
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from subprocess import check_output
from RPi import GPIO
from tabulate import tabulate
from repositories.DataRepository import DataRepository
import time
import threading
GPIO.setmode(GPIO.BCM)
lijst_pinnen = [16, 12, 25, 24, 23, 26, 19, 13]
rs_pin = 21
e_pin = 20
servo_pin = 5
reed_contact= 6
reader = SimpleMFRC522()

def setup():
    GPIO.setup(lijst_pinnen, GPIO.OUT)
    GPIO.setup(rs_pin, GPIO.OUT)
    GPIO.setup(e_pin, GPIO.OUT)
    GPIO.setup(servo_pin, GPIO.OUT)
    GPIO.setup(reed_contact, GPIO.IN,pull_up_down=GPIO.PUD_UP)


def set_data_bits(value):
    mask = 0b00000001
    for index in range(0, 8):
        pin = lijst_pinnen[index]
        if (value & mask) > 0:
            GPIO.output(pin, 1)
        else:
            GPIO.output(pin, 0)
        mask = mask << 1


def send_instruction(value):
    GPIO.output(rs_pin, 0)
    GPIO.output(e_pin, 1)
    set_data_bits(value)
    GPIO.output(e_pin, 0)
    time.sleep(0.005)


def send_character(value):
    GPIO.output(rs_pin, 1)
    GPIO.output(e_pin, 1)
    set_data_bits(value)
    GPIO.output(e_pin, 0)
    time.sleep(0.005)


def write_message(value):
    i = 0
    for x in str(value):
        i += 1
        # print(x)
        if i == 17:
            # checken als de karakter op positie 17 zit
            send_instruction(0b10000000 | 0b01000000)
        send_character(ord(x))


def init_LCD(cursorAan, cursorBlink):
    send_instruction(0x38)
    send_instruction(0b00001100 | (cursorAan << 1) | (cursorBlink << 0))
    send_instruction(1)


# ip-adressen ophalen en eventueel printen
ips = check_output(['hostname', '--all-ip-addresses'])
ip = ips.decode(encoding='utf-8').strip()
ip_adresses = ip.split()
#################################
show_lan = True
list_ids = []
teller = 0
setup()
init_LCD(1, 1)
servo = GPIO.PWM(servo_pin, 50)
servo.start(7.5)
# servo.ChangeDutyCycle(12)  # 3 is 0 graden, 12 is 180 graden
last_lcd_write = 0
# print(servo)


def callback_reedcontact(channel):
    global teller
    teller += 1
    print(f"YEAS {teller}")

GPIO.add_event_detect(reed_contact, GPIO.RISING,callback=callback_reedcontact, bouncetime=10)

def lcd_ip():
    global show_lan, last_lcd_write  # globale variabelen oproepen in functie
    epoch_time = int(time.time())  # tijd in seconden sinds 1970
    if (epoch_time - last_lcd_write > 2):  # kijken als het verschil groter is dan 2 seconden
        if (not show_lan):  # eerst is de variabele show_lan true pas dan false
            init_LCD(0, 0)
            write_message(f"WLAN IP-adres:  {ip_adresses[1]}")

        if show_lan:  # dit wordt als eerste afgeprint
            init_LCD(0, 0)
            write_message(f"LAN IP-adres:   {ip_adresses[0]}")

        last_lcd_write = epoch_time  # tijd overschrijven
        show_lan = not show_lan


def display_id():
    global last_lcd_write,list_ids,servo # globale variabele oproepen in functie
    while True:
        id, text = reader.read_no_block()  # uitlezen van de id en text
        if (id is None):  # als er niets wordt uitgelezen
            lcd_ip()
            servo.stop()
        else:
            if str(id) in list_ids:
                print('RFID-tag', id)
                init_LCD(0, 0)
                write_message(f"Id: {id}")
                send_instruction(0b10000000 | 0b01000000)
                write_message(text.strip())
                servo.ChangeDutyCycle(12)
                res = DataRepository.read_gebruikers_by_rfid(str(id))
                print(f"--> {res['Voornaam']}")
            else:
                print('Onbekende persoon')
                init_LCD(0, 0)
                write_message(f"!! Onbekend !!")
            epoch_time = int(time.time())
            last_lcd_write = epoch_time


def multiprocess_display_ip():
    p1 = multiprocessing.Process(target=display_id)
    p1.start()


def read_gebruikers():
    global servo
    global list_ids
    alle_ids = DataRepository.read_rfid_alle_gebruikers()
    for id_items in alle_ids:
        ids = id_items['RFID-code']
        if ids not in list_ids:
            list_ids.append(ids)
    # print(list_ids)
    # print(alle_ids)


try:
    read_gebruikers()
    multiprocess_display_ip()
    while True:
        # servo.ChangeDutyCycle(12)
        # print('Open')
        # time.sleep(2)
        # servo.ChangeDutyCycle(7.5)
        # print('Toe')
        # time.sleep(2)
        pass
finally:
    init_LCD(0, 0)
    GPIO.cleanup()
