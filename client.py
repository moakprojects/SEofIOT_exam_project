import socket
import pycom
import time
from pysense import Pysense
from LTR329ALS01 import LTR329ALS01
from SI7006A20 import SI7006A20
import json
import struct
from machine import Pin
from machine import ADC
from network import WLAN
import machine

pycom.heartbeat(False)

wifi_ssid = '########'
wifi_pass = '########'

if machine.reset_cause() != machine.SOFT_RESET:
    wlan = WLAN(mode=WLAN.STA)
    wlan.connect(wifi_ssid, auth=(WLAN.WPA2, wifi_pass), timeout=5000)

    while not wlan.isconnected():
        machine.idle()

print('Connected to Wifi\n')
print(wlan.ifconfig())

rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
time.timezone(7200)

py = Pysense()
lt = LTR329ALS01(py)
hu = SI7006A20(py)

p_out = Pin('P19', mode=Pin.OUT)
p_out.value(1)
p_out.value(0)
p_out.toggle()
p_out(True)

adc = ADC(id=0)
apin = adc.channel(pin='P16')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('########', 1234))

for x in range(10):
    light = lt.light()
    hum = hu.humidity()
    volt = apin.voltage()
    current_t = time.localtime()

    data = {'t':current_t,'b':light[0],'r':light[1],'h':hum,'v':volt}
    data_send = json.dumps(data)

    s.send(data_send)
    command = s.recv(1).decode("utf-8")
    if command == '1':
        pycom.rgbled(0xffffff)
    elif command == '2':
        pycom.rgbled(0x888888)
    elif command == '3':
        pycom.rgbled(0x000000)
    time.sleep(300)

s.close()
