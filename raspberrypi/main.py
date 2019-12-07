#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import json
import yesno

ENDPOINT="beam.soracom.io"
PORT=1883
TOPIC="yesno/result"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    json_str = str(msg.payload)
    print(msg.topic+" "+json_str)
    json_dic = json.loads(json_str)
    score = json_dic["score"]
    num_all = json_dic["detail"]["total"]
    num_yes = json_dic["detail"]["yes"]
    num_no = json_dic["detail"]["no"]
    yesno.showResult(score, num_all, num_yes, num_no)
    print("end on_message")

def getMqttClient(endpoint, port):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(endpoint, port, 60)
    return client

if __name__ == "__main__":
    client = getMqttClient(ENDPOINT, PORT)
    client.loop_forever()

