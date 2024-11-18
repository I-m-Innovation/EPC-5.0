# Generated by Django 5.1.3 on 2024-11-11 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EPC_5_0_v02', '0003_alter_offerta_slug'),
    ]

    operations = [
        migrations.RenameField(
            model_name='offerta',
            old_name='prezzo_fv',
            new_name='aliquota',
        ),
        migrations.RenameField(
            model_name='offerta',
            old_name='prezzo_storage',
            new_name='consumi_cliente',
        ),
        migrations.RenameField(
            model_name='offerta',
            old_name='prezzo_trainante',
            new_name='costi_energia_cliente',
        ),
        migrations.AddField(
            model_name='offerta',
            name='costo_fv',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='offerta',
            name='costo_storage',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='offerta',
            name='costo_totale',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='offerta',
            name='costo_trainante',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='offerta',
            name='crediti_fv',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='offerta',
            name='crediti_storage',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='offerta',
            name='crediti_totale',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='offerta',
            name='crediti_trainante',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='offerta',
            name='risparmio_energetico_trainante',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='offerta',
            name='tariffa_energia_cliente',
            field=models.FloatField(null=True),
        ),
    ]