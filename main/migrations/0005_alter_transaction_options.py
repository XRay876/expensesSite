# Generated by Django 5.1.1 on 2024-09-29 23:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_moneyblock_currency'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ['-date']},
        ),
    ]
