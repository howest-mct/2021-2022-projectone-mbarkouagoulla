import time
import RPi.GPIO as GPIO
import threading
import multiprocessing
from multiprocessing import Value
from mfrc522 import SimpleMFRC522
from subprocess import check_output
from tabulate import tabulate
import json
import os
from requests import get
from repositories.DataRepository import DataRepository
from helpers.klasse_lcd import LCD
from helpers.klasse_servo import SERVO
from flask_cors import CORS
from flask_socketio import SocketIO, emit, send
from flask import Flask, jsonify, request
from selenium import webdriver
from datetime import datetime
from helpers.klasse_hx711 import HX711
#######IN-OUT raspberry & variabelen#########
GPIO.setmode(GPIO.BCM)
lijst_pinnen = [16, 12, 25, 24, 23, 26, 19, 13]
rs_pin = 21
e_pin = 20

servo_pin = 5
servo_status = None
teller = 0
poweroff_fysiek = 6
reed_contact = 4
show_lan = True
list_ids = []
nieuwe_lijst = []
update_lijst= []
start_time = None
magneet_waarde = 1
button_waarde = 1
last_lcd_write = 0
reader = SimpleMFRC522()
lcd = LCD(lijst_pinnen, rs_pin, e_pin)
servo = SERVO(servo_pin)
hx = HX711(dout_pin=27, pd_sck_pin=17)
#################################
rfid_data = Value('d', 0)
rfid_user = Value('d', 0)
servo_value= Value('d', 0)
gewicht_value = Value('d',0)
add_user_value = Value('d',0)
deleted_user = Value('d', 0)
new_scanned_user = ''
gewicht = 0
vorige_waarde = 0
hulp_magneet = 0
#######GPIO-settings#############


def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(reed_contact, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(poweroff_fysiek, GPIO.IN, pull_up_down=GPIO.PUD_UP)


#################################
setup_gpio()

lcd.init_LCD(1, 1)

# Code voor Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'geheim!'
socketio = SocketIO(app, cors_allowed_origins="*", logger=False,
                    engineio_logger=False, ping_timeout=1)

CORS(app)


########IP-adressen##########
# ip-adressen ophalen en eventueel printen
def ip_adressen():
    global socketio
    ips = check_output(['hostname', '-I'])
    ip = ips.decode(encoding='utf-8').strip()
    ip_adresses = ip.split()
    # print(ip_adresses)
    return ip_adresses
#################################

def magneet_nok():
    global magneet_waarde
    now = datetime.now()
    correct_format_date = now.strftime("%d/%m/%Y %H:%M:%S")
    socketio.emit('magneetcontact_nok', {
                  'waarde': magneet_waarde, "datetime": correct_format_date}, broadcast=True)
    DataRepository.add_history_sensors(2, now, 0)


def magneet_ok():
    global magneet_waarde
    now = datetime.now()
    correct_format_date = now.strftime("%d/%m/%Y %H:%M:%S")
    socketio.emit('magneetcontact_ok', {
                  'waarde': magneet_waarde, "datetime": correct_format_date}, broadcast=True)
    DataRepository.add_history_sensors(2, now, 1)


def callback_reedcontact(channel):
    global magneet_waarde, reed_contact
    time.sleep(0.05)
    magneet_waarde = GPIO.input(reed_contact)
    print(f'reed>{magneet_waarde}')
    if magneet_waarde == 1:
        magneet_nok()
    elif magneet_waarde == 0:
        magneet_ok()


def callback_reedcontact1(channel):
    global poweroff_fysiek,button_waarde, os
    time.sleep(0.05)
    button_waarde = GPIO.input(poweroff_fysiek)
    if button_waarde == 1:
        print('sudo poweroff now...')
        lcd.init_LCD(0, 0)
        lcd.write_message(f"Powering off in 3 seconds")
        time.sleep(1)
        lcd.init_LCD(0, 0)
        time.sleep(3)
        # os.system('sudo poweroff')
    elif button_waarde == 0:
        print('Werking')

GPIO.add_event_detect(reed_contact, GPIO.BOTH,
                      callback=callback_reedcontact, bouncetime=100)
GPIO.add_event_detect(poweroff_fysiek, GPIO.FALLING ,
                      callback=callback_reedcontact1, bouncetime=300)


def lcd_ip(servo_status,gewicht_lcd):
    # globale variabelen oproepen in functie
    global show_lan, last_lcd_write
    ip_adresses = ip_adressen()
    epoch_time = int(time.time())  # tijd in seconden sinds 1970
    if servo_status.value == 1.0:
        if (epoch_time - last_lcd_write > 2):  # kijken als het verschil groter is dan 2 seconden
            if (not show_lan):  # eerst is de variabele show_lan true pas dan false
                if not ip_adresses:
                    lcd.init_LCD(0, 0)
                    lcd.write_message(f"Getting IP-adres")
                else:
                    lcd.init_LCD(0, 0)
                    lcd.write_message(f"WLAN IP-adres:  {ip_adresses[0]}")
            if show_lan:  # dit wordt als eerste afgeprint
                if gewicht_lcd.value > 2.5:
                    print('GEWICHT')
                    lcd.init_LCD(0, 0)
                    lcd.write_message(f"Open the box    you got mail!")
                elif not gewicht_lcd.value :
                    lcd.init_LCD(0, 0)
                    lcd.write_message(f"Checking your   mail...")
                else:
                    lcd.init_LCD(0, 0)
                    lcd.write_message(f"It's all right  You have no mail")
            show_lan = not show_lan
            last_lcd_write = epoch_time  # tijd overschrijven
    else:
        if int(servo_status.value) == 2:
            lcd.init_LCD(0, 0)
            lcd.write_message(f"Door is open")
            last_lcd_write = epoch_time  # tijd overschrijven
        if int(servo_status.value) == 3:
            lcd.init_LCD(0, 0)
            lcd.write_message(f"Door is closed")
            last_lcd_write = epoch_time  # tijd overschrijven
        servo_status.value = 1.0


def display_id(shared_data, shared_user,shared_servo,gewicht_value,add_user_value,deleted_user):
    # globale variabele oproepen in functie
    global last_lcd_write, list_ids,socketio, teller, nieuwe_lijst, update_lijst
    while True:
        read_gebruikers()
        id_rfid, text = reader.read_no_block()  # uitlezen van de id_rfid en text
        teller += 1
        # print('ik luister naar scan', teller)
        # print('--->',teller)
        if (id_rfid is None):  # als er niets wordt uitgelezen
            lcd_ip(shared_servo,gewicht_value)
        else:
            if str(id_rfid) in nieuwe_lijst  and int(id_rfid) != deleted_user.value:
                res = DataRepository.read_gebruikerID_by_rfid(str(id_rfid))
                print('RFID-tag', id_rfid)
                print(f"--> {res}")
                now = datetime.now()
                id_user = res['GebruikerID']
                DataRepository.add_history_sensors(3,now,id_rfid)
                DataRepository.add_history_action(4,now,id_user)
                shared_data.value = id_rfid
                shared_user.value = id_user
            else:
                print('Onbekende persoon')
                add_user_value.value= id_rfid
                lcd.init_LCD(0, 0)
                lcd.write_message(f"!! Unknown user !!")
            epoch_time = int(time.time())
            last_lcd_write = epoch_time
            time.sleep(2)   



def servo_sluit():
    global start_time, servo, socketio, rfid_user, servo_status, test, servo_value
    start_time = None
    now = datetime.now()
    user_id = int(rfid_user.value)
    if user_id == 0 or user_id !=0:
        user_id = 5
    print(user_id)
    DataRepository.add_history_action(2, now, user_id)
    servo_value.value = 3
    socketio.emit("B2F_close", {'Deur': 'toe'}, broadcast=True)
    servo.sluit_deur()


def servo_open():
    global start_time, servo, socketio, rfid_user, servo_status,test
    start_time = None
    now = datetime.now()
    user_id = int(rfid_user.value)
    if user_id == 0  or user_id != 0:
        user_id = 5
    print(user_id)
    DataRepository.add_history_action(1, now, user_id)
    servo_value.value = 2
    socketio.emit("B2F_open", {'Deur': 'open'}, broadcast=True)
    servo.open_deur()


def check_process_data():
    global rfid_data, socketio, servo, rfid_user, gewicht, start_time, list_ids, add_user_value, new_scanned_user
    start_time = None
    while True:
        val = int(rfid_data.value)
        valuser = int(add_user_value.value)
        if start_time != None and ((time.time()-start_time) > 5):
            print('Automatisch')
            servo_sluit()
        if val != 0:
            print(val)
            rfid_data.value = 0
            servo_open()
            now = datetime.now()
            correct_format_date = now.strftime("%d/%m/%Y %H:%M:%S")
            start_time = time.time()
            time.sleep(2)
            if -2 < gewicht < 2:
                print('Posts LEeeg')
                servo_sluit()
        if valuser != 0:
            add_user_value.value = 0
            print('NIEUWE USER', valuser)
            new_scanned_user = valuser
            socketio.emit('rfid_new', {'rfid': valuser}, broadcast=True)


def multiprocess_display_ip():
    p1 = multiprocessing.Process(
        target=display_id, args=(rfid_data, rfid_user,servo_value,gewicht_value,add_user_value,deleted_user))
    p1.start()
    print("**** Starting DISPLAY ****")
    p2 = threading.Thread(target=check_process_data,args=())
    p2.start()
    print('*** Starting CHECK-DATA***')


def read_gebruikers():
    global list_ids, nieuwe_lijst
    alle_ids = DataRepository.read_rfid_alle_gebruikers()
    for id_items in alle_ids:
        ids = id_items['RFID-code']
        # if ids not in list_ids:
        list_ids.append(ids)
    nieuwe_lijst = list_ids
    # print(list_ids)
    # print(nieuwe_lijst)


def data_gewichtsensor():
    global gewicht
    global vorige_waarde
    global hx
    global socketio
    err = hx.zero()
    # check if successful
    if err:
        raise ValueError('Tare is unsuccessful.')
    reading = hx.get_raw_data_mean()
    if reading:
        print('Data subtracted by offset but still not converted to units:',
              reading)
    else:
        print('invalid data', reading)

    input('Leg iets op de weegschaal waarvan je het gewicht ongeveer weet:\n')
    reading = hx.get_data_mean()
    if reading:
        print('Mean value from HX711 subtracted by offset:', reading)
        known_weight_grams = input(
            'Geef in hoeveel gram het was en druk op Enter: ')
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
    # input('Press Enter to begin reading')
    print('Huidige gewicht op de weegschaal: ')
    while True:
        gewicht = hx.get_weight_mean(20)
        # now = datetime.now()
        # correct_format_date = now.strftime("%d/%m/%Y %H:%M:%S")
        time.sleep(0.5)
        print(gewicht)

        # if ((gewicht < (vorige_waarde -2) )or  (gewicht > (vorige_waarde + 2))):
        #     print(f"Gewicht: {gewicht}")
        #     print(vorige_waarde)
        #     socketio.emit('gewicht', {'waarde': round(
        #         gewicht, 2), "datetime": correct_format_date}, broadcast=True)
        # vorige_waarde = gewicht


def data_gewichtsensor_offset():
    global gewicht
    global gewicht_value
    global vorige_waarde
    global hx
    global socketio
    global rfid_user
    
    hx.set_offset(-512965)


    
    reading = 112129

    if reading:
        print('Mean value from HX711 subtracted by offset:', reading)
    
        known_weight_grams = 228
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
    # input('Press Enter to begin reading')
    print('Huidige gewicht op de weegschaal: ')
    while True:
        gewicht = hx.get_weight_mean(20)
        gewicht_value.value= gewicht
        print(gewicht)
        now = datetime.now()
        correct_format_date = now.strftime("%d/%m/%Y %H:%M:%S")
        if gewicht < 2.5:
            # gewicht = 0
            socketio.emit('leegpost', {'waarde': gewicht}, broadcast=True)
            user_id = int(rfid_user.value)
            if user_id != 0:
            # print(user_id)
                DataRepository.add_history_action(3,now,user_id)
                DataRepository.add_history_sensors(1, now, gewicht)
        else:
            socketio.emit('post', {'waarde': gewicht}, broadcast=True)
        # time.sleep(1)
        if ((gewicht < (vorige_waarde - 2)) or (gewicht > (vorige_waarde + 2)) or (vorige_waarde == 0)):
            print(f"Gewicht: {gewicht}")
            print(vorige_waarde)
            socketio.emit('gewicht', {'waarde': round(
                gewicht, 2), "datetime": correct_format_date}, broadcast=True)
            DataRepository.add_history_sensors(1,now,gewicht)
            vorige_waarde = gewicht


@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print(e)


@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."



@socketio.on('connect')
def initial_connection():
    global socketio
    callback_reedcontact(1)
    ip_adres = ip_adressen()
    print('A new client connect')
    gebruikers = DataRepository.read_gebruikers()
    history = DataRepository.read_history_action()
    new_history = json.dumps(history, indent=4, sort_keys=True, default=str)
    # print(tabulate(history))
    emit('Gebruikers', {'gebruikers': gebruikers}, broadcast=True)
    emit('ipadres', {'adres': ip_adres[0]}, broadcast=True)
    emit('History', {'history': new_history}, broadcast=True)


@socketio.on('F2B_open')
def switch_servo(payload):
    global servo, socketio
    servo_open()
    socketio.emit("B2F_open", {'Deur': 'open'}, broadcast=True)


@socketio.on('F2B_close')
def switch_servo(payload):
    global servo, socketio
    servo_sluit()
    socketio.emit("B2F_close", {'Deur': 'toe'}, broadcast=True)


@socketio.on('F2B_adduser')
def adduser(payload):
    global socketio, new_scanned_user
    deleted_user.value = 0
    now = datetime.now()
    correct_format_date = now.strftime("%d/%m/%Y %H:%M:%S")
    x = json.loads(payload)
    DataRepository.add_gebruiker(x['LName'], x['FNaam'], str(x['RFID']), x['Email'])
    res = DataRepository.read_gebruikerID_by_rfid(str(new_scanned_user))
    id_user = res['GebruikerID']
    DataRepository.add_history_action(5, now, id_user)
    socketio.emit("B2F_adduser_done")
    read_gebruikers()

@socketio.on('deleteGebruiker')
def deleteuser(payload):
    global socketio, update_lijst
    del_id = payload['id']
    deleted_user.value = int(del_id)
    DataRepository.delete_user(del_id)
    socketio.emit("B2F_deleteuser_done")
    new_ids = DataRepository.read_rfid_alle_gebruikers()
    for id_items in new_ids:
        ids = id_items['RFID-code']
        # if ids not in list_ids:
        update_lijst.append(ids)
    print('na delete', update_lijst)
    # read_gebruikers()

    # print('VERWIDJERdD',payload['id'])

@socketio.on('F2B_poweroff')
def poweroff(payload):
    global os
    print('Poweroff now....')
    print('sudo poweroff now...')
    lcd.init_LCD(0, 0)
    lcd.write_message(f"Powering off in 3 seconds")
    time.sleep(1)
    lcd.init_LCD(0, 0)
    time.sleep(3)
    # os.system('sudo poweroff')

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


def start_gewicht_thread_offset():
    print('*** Starting LOADCELL ****')
    loadcellThread = threading.Thread(
        target=data_gewichtsensor_offset, args=(), daemon=True)
    loadcellThread.start()


if __name__ == '__main__':
    try:
        read_gebruikers()
        # start_gewicht_thread()
        start_gewicht_thread_offset()
        start_chrome_thread()
        multiprocess_display_ip()
        socketio.run(app, debug=False, host='0.0.0.0')
    except KeyboardInterrupt as e:
        print(e)
    finally:
        lcd.init_LCD(0, 0)
        GPIO.cleanup()
