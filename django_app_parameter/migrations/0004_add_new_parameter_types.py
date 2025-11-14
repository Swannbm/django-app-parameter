# Manual migration to add new parameter types and update existing ones

from django.db import migrations, models


def update_date_and_time_values(apps, schema_editor):
    """Update existing DATE and TIME values to DAT and TIM"""
    Parameter = apps.get_model("django_app_parameter", "Parameter")

    # Update DATE to DAT
    Parameter.objects.filter(value_type="DATE").update(value_type="DAT")

    # Update TIME to TIM
    Parameter.objects.filter(value_type="TIME").update(value_type="TIM")


def reverse_date_and_time_values(apps, schema_editor):
    """Reverse: Update DAT and TIM back to DATE and TIME"""
    Parameter = apps.get_model("django_app_parameter", "Parameter")

    # Update DAT to DATE
    Parameter.objects.filter(value_type="DAT").update(value_type="DATE")

    # Update TIM to TIME
    Parameter.objects.filter(value_type="TIM").update(value_type="TIME")


class Migration(migrations.Migration):
    dependencies = [
        (
            "django_app_parameter",
            "0003_alter_parameter_value_type",
        ),
    ]

    operations = [
        # First, run the data migration to update existing values
        migrations.RunPython(
            update_date_and_time_values,
            reverse_code=reverse_date_and_time_values,
        ),
        # Then, alter the field to include all new types
        migrations.AlterField(
            model_name="parameter",
            name="value_type",
            field=models.CharField(
                choices=[
                    ("INT", "Nombre entier"),
                    ("STR", "Chaîne de caractères"),
                    ("FLT", "Nombre à virgule (Float)"),
                    ("DCL", "Nombre à virgule (Decimal)"),
                    ("JSN", "JSON"),
                    ("BOO", "Booléen"),
                    ("DAT", "Date (YYYY-MM-DD)"),
                    ("DTM", "Date et heure (ISO 8601)"),
                    ("TIM", "Heure (HH:MM:SS)"),
                    ("URL", "URL validée"),
                    ("EML", "Email validé"),
                    ("LST", "Liste (séparée par virgules)"),
                    ("DCT", "Dictionnaire JSON"),
                    ("PTH", "Chemin de fichier"),
                    ("DUR", "Durée (en secondes)"),
                    ("PCT", "Pourcentage (0-100)"),
                ],
                default="STR",
                max_length=3,
                verbose_name="Type de donnée",
            ),
        ),
    ]
