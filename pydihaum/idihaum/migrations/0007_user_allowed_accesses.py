# Generated by Django 5.0.7 on 2024-07-12 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('idihaum', '0006_access_reader'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='allowed_accesses',
            field=models.ManyToManyField(to='idihaum.access_reader'),
        ),
    ]
