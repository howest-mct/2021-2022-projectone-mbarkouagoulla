import time
import RPi.GPIO as GPIO
import threading
import multiprocessing
from multiprocessing import Value
from mfrc522 import SimpleMFRC522
from subprocess import check_output

from repositories.DataRepository import DataRepository
from helpers.klasse_lcd import LCD
from helpers.klasse_servo import SERVO
from flask_cors import CORS
from flask_socketio import SocketIO, emit, send
from flask import Flask, jsonify
from selenium import webdriver
from datetime import datetime
from helpers.klasse_hx711 import HX711
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
hx = HX711(dout_pin=27, pd_sck_pin=17)
#################################
rfid_data = Value('d', 0)
#######GPIO-settings#############


def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setup(reed_contact, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#################################


########IP-adressen##########
# ip-adressen ophalen en eventueel printen
def ip_adressen():
    ips = check_output(['hostname', '--all-ip-addresses'])
    ip = ips.decode(encoding='utf-8').strip()
    ip_adresses = ip.split()
    # print(ip_adresses)
    return ip_adresses


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
    global waarde, socketio
    waarde = 1
    print(f'--->{waarde}')
    if waarde == 1:
        now = datetime.now()
        correct_format_date = now.strftime("%d/%m/%Y %H:%M:%S")
        socketio.emit('magneetcontact', {
                      'waarde': waarde, "datetime": correct_format_date}, broadcast=True)


GPIO.add_event_detect(reed_contact, GPIO.RISING,
                      callback=callback_reedcontact, bouncetime=10000)


def lcd_ip():
    global show_lan, last_lcd_write  # globale variabelen oproepen in functie
    ip_adresses = ip_adressen()
    epoch_time = int(time.time())  # tijd in seconden sinds 1970
    if (epoch_time - last_lcd_write > 2):  # kijken als het verschil groter is dan 2 seconden
        if (not show_lan):  # eerst is de variabele show_lan true pas dan false
            lcd.init_LCD(0, 0)
            lcd.write_message(f"WLAN IP-adres:  {ip_adresses[1]}")
        if show_lan:  # dit wordt als eerste afgeprint
            lcd.init_LCD(0, 0)
            lcd.write_message(f"LAN IP-adres:   {ip_adresses[0]}")

        last_lcd_write = epoch_time  # tijd overschrijven
        show_lan = not show_lan


def display_id(shared_data):
    # globale variabele oproepen in functie
    global last_lcd_write, list_ids
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
                print(f"--> {res['Voornaam']}")
                shared_data.value = id_rfid
            else:
                print('Onbekende persoon')
                lcd.init_LCD(0, 0)
                lcd.write_message(f"!! Onbekend !!")
            epoch_time = int(time.time())
            last_lcd_write = epoch_time
            time.sleep(2)


def check_process_data():
    global rfid_data, socketio, servo
    while True:
        val = int(rfid_data.value)
        if val != 0:
            print(val)
            rfid_data.value = 0
            now = datetime.now()
            correct_format_date = now.strftime("%d/%m/%Y %H:%M:%S")
            socketio.emit('rfid_gebruiker', {
                          'rfid': val, "datetime": correct_format_date}, broadcast=True)
            servo.open_deur()
            time.sleep(2)
            servo.sluit_deur()
            time.sleep(1)


def multiprocess_display_ip():
    p1 = multiprocessing.Process(target=display_id, args=(rfid_data,))
    p1.start()
    print("**** Starting DISPLAY ****")
    p1 = threading.Thread(target=check_process_data,
                          args=(), daemon=True)
    p1.start()


def read_gebruikers():
    global list_ids
    alle_ids = DataRepository.read_rfid_alle_gebruikers()
    for id_items in alle_ids:
        ids = id_items['RFID-code']
        if ids not in list_ids:
            list_ids.append(ids)
    # print(list_ids)


def data_gewichtsensor():
    global hx
    err = hx.zero()
    # check if successful
    if err:
        raise ValueError('Tare is unsuccessful.')
    # reading = 49342
    reading = hx.get_raw_data_mean()
    if reading:
        print('Data subtracted by offset but still not converted to units:',
              reading)
    else:
        print('invalid data', reading)

    input('Leg iets op de weegschaal waarvan je het gewicht ongeveer weet:\n')
    # reading = 27590
    reading = hx.get_data_mean()
    if reading:
        print('Mean value from HX711 subtracted by offset:', reading)
        # known_weight_grams = 5
        known_weight_grams = input('Geef in hoeveel gram het was en druk op Enter: ')
        try:
            value = float(known_weight_grams)
            print(value, 'grams')
        except ValueError:
            print('Expected integer or float and I have got:',
                  known_weight_grams)

        ratio = reading / value  # calculate the ratio for channel A and gain 128
        hx.set_scale_ratio(ratio)  # set ratio for current channel
        print('Ratio is set.')
    else:
        raise ValueError(
            'Cannot calculate mean value. Try debug mode. Variable reading:', reading)
    input('Press Enter to begin reading')
    print('Huidige gewicht op de weegschaal: ')
    while True:
        print(hx.get_weight_mean(20), 'g')
        time.sleep(2)


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


def start_gewicht_thread():
    print('*** Starting LOADCELL ****')
    loadcellThread = threading.Thread(
        target=data_gewichtsensor, args=(), daemon=True)
    loadcellThread.start()


if __name__ == '__main__':
    try:
        read_gebruikers()
        # start_gewicht_thread()
        start_chrome_thread()
        multiprocess_display_ip()
        socketio.run(app, debug=False, host='0.0.0.0')
    except KeyboardInterrupt as e:
        print(e)
    finally:
        lcd.init_LCD(0, 0)
        GPIO.cleanup()
