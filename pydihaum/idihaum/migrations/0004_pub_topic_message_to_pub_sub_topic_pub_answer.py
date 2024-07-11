# Generated by Django 5.0.6 on 2024-07-11 12:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('idihaum', '0003_pub_topic_sub_topic'),
    ]

    operations = [
        migrations.AddField(
            model_name='pub_topic',
            name='message_to_pub',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sub_topic',
            name='pub_Answer',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='idihaum.pub_topic'),
            preserve_default=False,
        ),
    ]
