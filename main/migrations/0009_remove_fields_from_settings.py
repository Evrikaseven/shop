# Generated by Django 2.2.3 on 2019-10-10 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20191001_1645'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='settingoption',
            name='contacts',
        ),
        migrations.RemoveField(
            model_name='settingoption',
            name='partnership',
        ),
        migrations.AlterField(
            model_name='settingoption',
            name='s_value',
            field=models.TextField(blank=True, default=''),
        ),
    ]
