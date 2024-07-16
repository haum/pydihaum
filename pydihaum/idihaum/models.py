from django.db import models


class Access_reader(models.Model):
    label = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    listen_topic = models.CharField(max_length=255) # topic recevant l ID de la carte
    answer_topic = models.CharField(max_length=255) # topic action du reader
    message_topic = models.CharField(max_length=255) # message pour action du reader

    def __str__(self):
        return str(self.label)


class User(models.Model):
    name = models.CharField(blank=True, null=True, max_length=255)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    allowed_accesses = models.ManyToManyField(Access_reader, blank=True)

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
    reader = models.ForeignKey(Access_reader, null=True, on_delete=models.SET_NULL)
    unknown_card = models.CharField(blank=True, null=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comment = models.CharField(blank=True, null=True, max_length=255)

    def __str__(self):
        return str(self.user) + ' at ' + str(self.created_at)
