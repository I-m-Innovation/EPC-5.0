# Generated by Django 5.1.3 on 2024-11-11 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EPC_5_0_v02', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offerta',
            name='potenza_installata',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='offerta',
            name='prezzo_fv',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='offerta',
            name='prezzo_storage',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='offerta',
            name='prezzo_trainante',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='offerta',
            name='producibilità_specifica',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='offerta',
            name='produzione_annua',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='offerta',
            name='storage_installato',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='offerta',
            name='tipologia_moduli',
            field=models.FloatField(null=True),
        ),
    ]