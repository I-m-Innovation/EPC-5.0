# Generated by Django 5.1.3 on 2024-11-17 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EPC_5_0_v02', '0026_offerta_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offerta',
            name='slug',
            field=models.SlugField(),
        ),
    ]