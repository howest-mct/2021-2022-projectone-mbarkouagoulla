import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from subprocess import check_output
from RPi import GPIO
from tabulate import tabulate
from repositories.DataRepository import DataRepository
import time
GPIO.setmode(GPIO.BCM)
lijst_pinnen = [16, 12, 25, 24, 23, 26, 19, 13]
rs_pin = 21
e_pin = 20

reader = SimpleMFRC522()


def setup():
    GPIO.setup(lijst_pinnen, GPIO.OUT)
    GPIO.setup(rs_pin, GPIO.OUT)
    GPIO.setup(e_pin, GPIO.OUT)

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
    time.sleep(0.1)

def send_character(value):
    GPIO.output(rs_pin, 1)
    GPIO.output(e_pin, 1)
    set_data_bits(value)
    GPIO.output(e_pin, 0)
    time.sleep(0.1)


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


ips = check_output(['hostname', '--all-ip-addresses'])
ip = ips.decode(encoding='utf-8').strip()
ip_adresses= ip.split()
print(ip_adresses[1])

setup()
init_LCD(1, 1)

try:
    # write_message(f"Mijn IP-adres:  {ip_adresses[1]}")
    # print('Scan je badge:')
    # id_code, text = reader.read()
    # print(f"Identificatiecode: {id_code}")
    # print(f"Gebruikersnaam: {text}")
    # gebruiker = text.strip()
    # print(type(gebruiker))
    # print(type(id_code))
    # x= str(id_code)
    voorbeeld_rfid = str(384580474190)
    # print(type(x))
    # init_LCD(0,0)
    # write_message(f"ID: {id}")
    # send_instruction(0b10000000 | 0b01000000)
    # write_message(text.strip())
    # time.sleep(1)
    # init_LCD(0,0)
    # DataRepository.update_rfid_gebruiker(gebruiker,x)
    # rfid = DataRepository.read_rfid_gebruiker(gebruiker)
    rfid_iedereen = DataRepository.read_rfid_alle_gebruikers()
    for gebruiker in rfid_iedereen:
        rfid_gebruiker = gebruiker["RFID-code"]
        # print(gebruiker["RFID-code"])
        if voorbeeld_rfid == rfid_gebruiker:
            print('OK')
    # if str(voorbeeld_rfid) in rfid_iedereen:
    #     print('Gebruiker zit er in')
    # else:
    #     print('Onbekende gebruiker')
    # print(tabulate(rfid_iedereen,headers="keys"))
    # print(rfid["RFID-code"])
    # write_message(f"Mijn IP-adres:  {ip_adresses[1]}")
    # data = DataRepository.read_gebruikers()
    # data1 = DataRepository.read_gebruikers_by_id(1)
    # print(data)
    # print(data1)
    # print(tabulate(data,headers="keys"))
    # print(tabulate(data1,headers="keys"))
finally:
    GPIO.cleanup()
