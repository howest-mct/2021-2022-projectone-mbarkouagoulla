import time
import RPi.GPIO as GPIO
import threading
import multiprocessing

from mfrc522 import SimpleMFRC522
from subprocess import check_output
from datetime import datetime
now = datetime.now()
correct_format_date = now.strftime("%d/%m/%Y %H:%M:%S")
from repositories.DataRepository import DataRepository
from helpers.klasse_lcd import LCD
from helpers.klasse_servo import SERVO
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
waarde = 1
last_lcd_write = 0
reader = SimpleMFRC522()
lcd = LCD(lijst_pinnen, rs_pin, e_pin)
servo = SERVO(servo_pin)
#################################

#######GPIO-settings#############


def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setup(reed_contact, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#################################


########IP-adressen##########
# ip-adressen ophalen en eventueel printen
ips = check_output(['hostname', '--all-ip-addresses'])
ip = ips.decode(encoding='utf-8').strip()
ip_adresses = ip.split()
print(ip_adresses)
#################################
setup_gpio()
lcd.init_LCD(1, 1)

# Code voor Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'geheim!'
socketio = SocketIO(app, cors_allowed_origins="*", logger=False,
                    engineio_logger=False, ping_timeout=1)

CORS(app)


def callback_reedcontact(channel):
    global waarde
    waarde = 1
    print(waarde)
    # teller += 1
    # print(f"YEAS {teller}")


socketio.emit("magneetcontact", {'waarde': waarde}, broadcast=True)

GPIO.add_event_detect(reed_contact, GPIO.RISING,
                      callback=callback_reedcontact, bouncetime=1000)


def lcd_ip():
    global show_lan, last_lcd_write  # globale variabelen oproepen in functie
    epoch_time = int(time.time())  # tijd in seconden sinds 1970
    if (epoch_time - last_lcd_write > 1):  # kijken als het verschil groter is dan 2 seconden
        if (not show_lan):  # eerst is de variabele show_lan true pas dan false
            # init_LCD(0, 0)
            # write_message(f"WLAN IP-adres:  {ip_adresses[1]}")
            lcd.init_LCD(0, 0)
            lcd.write_message(f"WLAN IP-adres:  {ip_adresses[1]}")

        if show_lan:  # dit wordt als eerste afgeprint
            # init_LCD(0, 0)
            # write_message(f"LAN IP-adres:   {ip_adresses[0]}")
            lcd.init_LCD(0, 0)
            lcd.write_message(f"LAN IP-adres:   {ip_adresses[0]}")

        last_lcd_write = epoch_time  # tijd overschrijven
        show_lan = not show_lan


def display_id():
    # globale variabele oproepen in functie
    global last_lcd_write, list_ids, servo, socketio
    while True:
        id_rfid, text = reader.read_no_block()  # uitlezen van de id_rfid en text
        if (id_rfid is None):  # als er niets wordt uitgelezen
            lcd_ip()
        else:
            if str(id_rfid) in list_ids:
                print('RFID-tag', id_rfid)
                lcd.init_LCD(0, 0)
                lcd.write_message(f"Id: {id_rfid}")
                lcd.send_instruction(0b10000000 | 0b01000000)
                lcd.write_message(text.strip())
                res = DataRepository.read_gebruikers_by_rfid(str(id_rfid))
                socketio.emit('rfid_gebruiker', {'data':{'id':id_rfid,'datum':correct_format_date}}, broadcast=True)
                print(f"--> {res['Voornaam']}")
            else:
                print('Onbekende persoon')
                lcd.init_LCD(0, 0)
                lcd.write_message(f"!! Onbekend !!")
            epoch_time = int(time.time())
            last_lcd_write = epoch_time


def multiprocess_display_ip():
    # p1 = multiprocessing.Process(target=display_id)
    # p1.start()
    # print("**** Starting CHROME ****")
    p1 = threading.Thread(
        target=display_id, args=(), daemon=True)
    p1.start()


def read_gebruikers():
    global list_ids
    alle_ids = DataRepository.read_rfid_alle_gebruikers()
    for id_items in alle_ids:
        ids = id_items['RFID-code']
        if ids not in list_ids:
            list_ids.append(ids)
    # print(list_ids)


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
    emit('Gebruikers', {'gebruikers': gebruikers}, broadcast=True)


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
        # servo.open_deur()
        # servo.sluit_deur()
        read_gebruikers()
        start_chrome_thread()
        multiprocess_display_ip()
        socketio.run(app, debug=False, host='0.0.0.0')
    except KeyboardInterrupt as e:
        print(e)
    finally:
        lcd.init_LCD(0, 0)
        GPIO.cleanup()
