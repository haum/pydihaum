#! /usr/bin/env python
# -*- coding:utf8 -*-
#
# mqtt.py
#
# Copyright © 2024 Mathieu Gaborit (matael) <mathieu@matael.org>
#
# Licensed under the "THE BEER-WARE LICENSE" (Revision 42):
# Mathieu (matael) Gaborit wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer or coffee in return
#

from django.conf import settings
import paho.mqtt.client as mqtt

from .models import Card, User, Log


def on_connect(mqtt_client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe('haum/gachaum/tag/uid')
   else:
       print('Bad connection. Code:', rc)


def on_message(mqtt_client, userdata, msg):
   print(f'Received message on topic: {msg.topic} with payload: {msg.payload}')
   if msg.topic == 'haum/gachaum/tag/uid':
       uid = msg.payload.decode('utf-8')
       card = Card.objects.filter(uid=uid).first()
       if card:
           user = card.user
           if not card.active:
               Log(user=user, card=card, comment='Denied: inactive card').save()
           else:
               if user and not user.active:
                   Log(user=user, card=card, comment='Denied: inactive user').save()
               else:
                   Log(user=user, card=card).save()
                   mqtt_client.publish('haum/gachaum/strike', 'open')
                   print(f'User {user} logged in')
       else:
           print(f'No card found for uid {uid}')
           Log(unknown_card=uid).save()

def initialize_mqtt():
    client = mqtt.Client()
    mqtt_user, mqtt_pass = getattr(settings, 'MQTT_USER', None), getattr(settings, 'MQTT_PASS', None)
    client.username_pw_set(mqtt_user, mqtt_pass )

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(
        host=settings.MQTT_HOST,
        port=settings.MQTT_PORT,
        keepalive=settings.MQTT_KEEPALIVE
    )
    client.loop_start()

