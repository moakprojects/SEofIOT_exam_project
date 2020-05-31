import socket
import json
import struct
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import time

cred = credentials.Certificate('service.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = socket.gethostbyname(socket.gethostname())
port = 1234

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(5)
clientsocket, address = s.accept()

while True:
    data = clientsocket.recv(1024).decode()
    d = json.loads(data)
    print(d)
    d["t"].append(0)
    date_str = time.strftime("%Y-%m-%d %H:%M:%S", tuple(d["t"]))
    temp=0.0685*d['v']-27.2
    doc_ref = db.collection(u'fromPycom').document(date_str)
    doc_ref.set({
        u'time': date_str,
        u'temp': temp,
        u'light_b': d['b'],
        u'light_r': d['r'],
        u'hum': d['h'],
    })
    now = datetime.now()
    currentHour = now.hour + 2

    set_ref = db.collection(u'setpoints').document(str(currentHour)).get()
    command = "0"
    if not (set_ref.to_dict() is None):
        if d["b"] + 10 < set_ref.to_dict()["light"]:
            command = "1"
        elif d["b"] < set_ref.to_dict()["light"]:
            command = "2"
        else:
            command = "3"
    clientsocket.send(bytes(command, "utf-8"))
