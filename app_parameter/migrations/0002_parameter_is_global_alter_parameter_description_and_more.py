# Generated by Django 4.0.2 on 2022-02-22 23:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_parameter', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameter',
            name='is_global',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='parameter',
            name='description',
            field=models.TextField(blank=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='parameter',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Nom'),
        ),
        migrations.AlterField(
            model_name='parameter',
            name='value',
            field=models.CharField(max_length=250, verbose_name='Valeur'),
        ),
        migrations.AlterField(
            model_name='parameter',
            name='value_type',
            field=models.CharField(choices=[('INT', 'Nombre entier'), ('STR', 'Chaîne de caractères'), ('FLT', 'Nombre à virgule (Float)'), ('DCL', 'Nombre à virgule (Decimal)'), ('JSN', 'JSON')], default='STR', max_length=3, verbose_name='Type de donnée'),
        ),
    ]
