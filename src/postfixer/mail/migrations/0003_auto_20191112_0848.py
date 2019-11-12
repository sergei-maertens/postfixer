# Generated by Django 2.2.1 on 2019-11-12 07:48

import django.core.validators
from django.db import migrations, models
import postfixer.mail.validators
import re


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0002_auto_20190601_0726'),
    ]

    operations = [
        migrations.CreateModel(
            name='VirtualMailbox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_part', models.CharField(max_length=255, validators=[postfixer.mail.validators.validate_lowercase, django.core.validators.RegexValidator(regex=re.compile('(^[-!#$%&\'*+/=?^_`{}|~0-9A-Z]+(\\.[-!#$%&\'*+/=?^_`{}|~0-9A-Z]+)*\\Z|^"([\\001-\\010\\013\\014\\016-\\037!#-\\[\\]-\\177]|\\\\[\\001-\\011\\013\\014\\016-\\177])*"\\Z)', 2))], verbose_name='user part')),
                ('domain_part', models.CharField(max_length=255, validators=[postfixer.mail.validators.validate_lowercase, django.core.validators.RegexValidator(regex=re.compile('((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\\.)+)(?:[A-Z0-9-]{2,63}(?<!-))\\Z', 2))], verbose_name='domain part')),
                ('password', models.CharField(blank=True, max_length=255, verbose_name='password')),
                ('comments', models.TextField(blank=True, verbose_name='comments')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
            ],
            options={
                'verbose_name': 'virtual mailbox',
                'verbose_name_plural': 'virtual mailboxes',
            },
        ),
        migrations.AddConstraint(
            model_name='virtualmailbox',
            constraint=models.UniqueConstraint(fields=('user_part', 'domain_part'), name='unique_email'),
        ),
    ]