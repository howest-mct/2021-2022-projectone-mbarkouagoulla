import multiprocessing
import RPi.GPIO as GPIO
import time
import threading
from mfrc522 import SimpleMFRC522
from subprocess import check_output
from tabulate import tabulate
from repositories.DataRepository import DataRepository
from helpers.klasseknop import Button

from flask_cors import CORS
from flask_socketio import SocketIO, emit, send
from flask import Flask, jsonify
from selenium import webdriver
#######IN-OUT raspberry & variabelen#########
GPIO.setmode(GPIO.BCM)
lijst_pinnen = [16, 12, 25, 24, 23, 26, 19, 13]
rs_pin = 21
e_pin = 20
servo_pin = 5
reed_contact = 6
show_lan = True
list_ids = []
teller = 0
last_lcd_write = 0
reader = SimpleMFRC522()
#################################



#######GPIO-settings#############
def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setup(lijst_pinnen, GPIO.OUT)
    GPIO.setup(rs_pin, GPIO.OUT)
    GPIO.setup(e_pin, GPIO.OUT)
    GPIO.setup(servo_pin, GPIO.OUT)
    GPIO.setup(reed_contact, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#################################


#######DISPLAY-settings########
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
#################################



########IP-adressen##########
# ip-adressen ophalen en eventueel printen
ips = check_output(['hostname', '--all-ip-addresses'])
ip = ips.decode(encoding='utf-8').strip()
ip_adresses = ip.split()
# print(ip_adresses)
#################################
setup_gpio()
init_LCD(1, 1)
servo = GPIO.PWM(servo_pin, 50)
servo.start(7.5)
# servo.ChangeDutyCycle(12)  # 3 is 0 graden, 12 is 180 graden



def callback_reedcontact(channel):
    global teller
    teller += 1
    print(f"YEAS {teller}")


GPIO.add_event_detect(reed_contact, GPIO.RISING,
                      callback=callback_reedcontact, bouncetime=10)


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
    global last_lcd_write, list_ids, servo  # globale variabele oproepen in functie
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
    while True:
        pass


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

# Code voor Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'geheim!'
socketio = SocketIO(app, cors_allowed_origins="*", logger=False,
                    engineio_logger=False, ping_timeout=1)

CORS(app)


@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print(e)


@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."

@socketio.on('connect')
def initial_connection():
    print('A new client connect')
    gebruikers = DataRepository.read_gebruikers()
    emit('Gebruikers',{'gebruikers':gebruikers},broadcast=True)


def start_chrome_kiosk():
    import os

    os.environ['DISPLAY'] = ':0.0'
    options = webdriver.ChromeOptions()
    # options.headless = True
    # options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-extensions")
    # options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    # options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--kiosk')
    # chrome_options.add_argument('--no-sandbox')
    # options.add_argument("disable-infobars")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    driver.get("http://localhost")
    while True:
        pass


def start_chrome_thread():
    print("**** Starting CHROME ****")
    chromeThread = threading.Thread(
    target=start_chrome_kiosk, args=(), daemon=True)
    chromeThread.start()


if __name__ == '__main__':
    try:
        read_gebruikers()
        start_chrome_thread()
        multiprocess_display_ip()
        # socketio.run(app, debug=False, host='0.0.0.0')
    except KeyboardInterrupt as e:
        print(e)
    finally:
        init_LCD(0, 0)
        GPIO.cleanup()
