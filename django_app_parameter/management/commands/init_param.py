import logging

from django.core.management.base import BaseCommand

from django_app_parameter.models import Parameter


logger = logging.getLogger("management.commands")


class Command(BaseCommand):
    help = "Reset all projects data, usefull when updating all precalculated fields"

    def handle(self, *args, **options):
        logger.info("Add new application parameters")
        new_params = [
            {
                "name": "Adresse e-mail de l'équipe",
                "slug": "TEAM_EMAIL",
                "value_type": Parameter.TYPES.STR,
            },
            {
                "name": "Titre du blog",
                "slug": "BLOG_TITLE",
                "value_type": Parameter.TYPES.STR,
                "description": "Il est affiché en haut à gauche, dans la barre de menu",
                "is_global": True,
            },
            {
                "name": "Url du site",
                "slug": "SITE_URL",
                "value_type": Parameter.TYPES.STR,
            },
        ]
        for param in new_params:
            result = Parameter.objects.create_if_not_exists(param)
            logger.info("Added %s with result=%s", param["slug"], result)
        logger.info("End adding new parameters")
