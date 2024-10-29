# Generated by Django 5.1 on 2024-10-28 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elaborazione', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='impianto',
            name='costo_impianto',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='impianto',
            name='costo_totale',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='impianto',
            name='produzione_annua',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='impianto',
            name='storage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
    ]
