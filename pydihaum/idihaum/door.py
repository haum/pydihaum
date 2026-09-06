# -*- coding: utf-8 -*-
"""Commande d'ouverture de la gâche.

Publie un message MQTT ponctuel, sans réutiliser le client de `mqtt.py` : celui-ci
vit dans un thread démarré par `apps.ready()`, qui n'existe que sous le serveur de
développement (garde `RUN_MAIN`). Passer par un client éphémère rend l'ouverture
manuelle indépendante du serveur d'application utilisé.

Le topic est paramétrable pour qu'un environnement de test ne puisse pas actionner
la vraie serrure : voir MQTT_TOPIC_STRIKE dans les réglages.
"""

from django.conf import settings
import paho.mqtt.publish as publish

from .models import Log

TOPIC_STRIKE_DEFAUT = 'haum/gachaum/strike'


def topic_strike():
    return getattr(settings, 'MQTT_TOPIC_STRIKE', TOPIC_STRIKE_DEFAUT)


def porte_reelle():
    """Vrai si le topic configuré est celui de la vraie gâche."""
    return topic_strike() == TOPIC_STRIKE_DEFAUT


def ouvrir(auteur=None):
    """Ouvre la porte et journalise qui l'a fait.

    Lève une exception si le broker est injoignable — l'appelant doit le dire à
    l'utilisateur plutôt que de laisser croire que la porte s'est ouverte.
    """
    auth = None
    if getattr(settings, 'MQTT_USER', None):
        auth = {'username': settings.MQTT_USER, 'password': settings.MQTT_PASS}

    publish.single(
        topic_strike(),
        'open',
        hostname=settings.MQTT_HOST,
        port=settings.MQTT_PORT,
        keepalive=settings.MQTT_KEEPALIVE,
        auth=auth,
    )

    qui = getattr(auteur, 'username', None) or 'inconnu'
    Log(comment=f'Ouverture manuelle par {qui}').save()
