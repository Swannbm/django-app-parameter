# Generated by Django 4.0.2 on 2023-10-18 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_app_parameter', '0002_parameter_is_global_alter_parameter_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parameter',
            name='value_type',
            field=models.CharField(choices=[('INT', 'Nombre entier'), ('STR', 'Chaîne de caractères'), ('FLT', 'Nombre à virgule (Float)'), ('DCL', 'Nombre à virgule (Decimal)'), ('JSN', 'JSON'), ('BOO', 'Booléen')], default='STR', max_length=3, verbose_name='Type de donnée'),
        ),
    ]
