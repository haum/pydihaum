#! /usr/bin/env python
# -*- coding:utf8 -*-
#
# legacy_import.py
#
# Copyright © 2024 Mathieu Gaborit (matael) <mathieu@matael.org>
#
# Licensed under the "THE BEER-WARE LICENSE" (Revision 42):
# Mathieu (matael) Gaborit wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer or coffee in return
#

from django.core.management.base import BaseCommand, CommandError
from idihaum.models import User, Card, Log

import sqlite3

class Command(BaseCommand):

    # take a database file as argument, open it and import tables cards, logs and users
    # into the django models

    def add_arguments(self, parser):
        parser.add_argument('dbfile', nargs='+', type=str)

    def handle(self, *args, **options):
        dbfile = options['dbfile'][0]

        conn = sqlite3.connect(dbfile)
        c = conn.cursor()

        usermap = {}
        cardmap = {}
        unknown_user = User(name='unknown', active=False)
        unknown_user.save()
        # import users
        c.execute('SELECT * FROM users order by id')
        for row in c.fetchall():
            u = User(
                name = row[1],
                active = True,
                created_at = row[2],
                updated_at = row[3]
            )
            u.save()
            usermap[row[0]] = u

        # import cards
        c.execute('SELECT * FROM cards')
        for row in c.fetchall():
            card = Card(
                uid = row[1],
                user = usermap.get(row[2], unknown_user),
                active = True,
                created_at = row[3],
                updated_at = row[4],
                label = row[5] if row[5] else 'imported'
            )
            card.save()
            cardmap[row[0]] = card

        # import logs
        c.execute('SELECT * FROM logs')
        for row in c.fetchall():
            log = Log(
                card = cardmap.get(row[1]),
                user = usermap.get(row[2]),
                unknown_card = row[3],
                created_at = row[4],
                updated_at = row[5],
                comment = "imported from legacy db"
            )
            log.save()

        conn.close()
        print('Import done')

