# Manual migration to create ParameterValidator model

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "django_app_parameter",
            "0004_add_new_parameter_types",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="ParameterValidator",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "validator_type",
                    models.CharField(
                        choices=[
                            ("MinValueValidator", "Valeur minimale"),
                            ("MaxValueValidator", "Valeur maximale"),
                            ("MinLengthValidator", "Longueur minimale"),
                            ("MaxLengthValidator", "Longueur maximale"),
                            ("RegexValidator", "Expression régulière"),
                            ("EmailValidator", "Validation email"),
                            ("URLValidator", "Validation URL"),
                            ("validate_slug", "Validation slug"),
                            ("validate_ipv4_address", "Adresse IPv4"),
                            ("validate_ipv6_address", "Adresse IPv6"),
                            (
                                "FileExtensionValidator",
                                "Extensions de fichier autorisées",
                            ),
                        ],
                        max_length=50,
                        verbose_name="Type de validateur",
                    ),
                ),
                (
                    "validator_params",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Paramètres JSON pour instancier le validateur (ex: {'limit_value': 100})",
                        verbose_name="Paramètres du validateur",
                    ),
                ),
                (
                    "parameter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="validators",
                        to="django_app_parameter.parameter",
                        verbose_name="Paramètre",
                    ),
                ),
            ],
            options={
                "verbose_name": "Validateur de paramètre",
                "verbose_name_plural": "Validateurs de paramètre",
                "ordering": ["order"],
            },
        ),
    ]
