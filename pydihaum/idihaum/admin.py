from django.contrib import admin

from .models import Card, User, Log

admin.site.register(Card)
admin.site.register(User)
admin.site.register(Log)
