# Generated by Django 5.1.3 on 2024-11-12 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EPC_5_0_v02', '0014_offerta_risparmio_totale_primo_anno'),
    ]

    operations = [
        migrations.AddField(
            model_name='offerta',
            name='risparmio_dieci_anni',
            field=models.FloatField(null=True),
        ),
    ]