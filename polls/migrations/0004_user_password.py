# Generated by Django 2.2.2 on 2019-07-30 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_auto_20190705_2105'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='password',
            field=models.CharField(default='password', max_length=200),
            preserve_default=False,
        ),
    ]