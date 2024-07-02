from django.db import models


class User(models.Model):
    name = models.CharField(blank=True, null=True, max_length=255)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Card(models.Model):
    uid = models.CharField(unique=True, max_length=255)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    label = models.CharField(max_length=255)

    def __str__(self):
        return str(self.uid) + ' - ' + str(self.user)


class Log(models.Model):
    card = models.ForeignKey(Card, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    unknown_card = models.CharField(blank=True, null=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comment = models.CharField(blank=True, null=True, max_length=255)

    def __str__(self):
        return str(self.user) + ' at ' + str(self.created_at)
