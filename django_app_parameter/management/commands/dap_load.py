"""Command to import parameters into the database

Arguments:
    --file: a json file with all the parameter to be added
    --no-update: flag to avoid updating existing parameters
    --json: dict containing a new parameter's values, can't be use with --file
"""

import argparse
import json
import logging
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from django_app_parameter.models import Parameter

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import parameters into the database"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--file",
            type=argparse.FileType("r"),
            help="json file containing a list of new parameters",
            default=argparse.SUPPRESS,
        )
        parser.add_argument("--no-update", action="store_const", const=True)
        parser.add_argument(
            "--json",
            type=json.loads,
            help="json string containing a list of new parameters",
            default=argparse.SUPPRESS,
        )

    def handle(self, *args: Any, **options: Any) -> None:
        logger.info("Load parameter start")
        # store opposite to flag
        do_update = not options.get("no_update", False)

        if "file" in options:
            logger.info("Read file %s", options["file"])
            # required check to be compatible with call_command()
            if isinstance(options["file"], str):
                options["file"] = open(options["file"])
            json_data = json.loads(options["file"].read())
            Parameter.objects.load_from_json(  # type: ignore[attr-defined]
                json_data, do_update=do_update
            )
        elif "json" in options:
            # required check to be compatible with call_command()
            if isinstance(options["json"], str):
                options["json"] = json.loads(options["json"])
            Parameter.objects.load_from_json(  # type: ignore[attr-defined]
                options["json"], do_update=do_update
            )
        logger.info("End load parameter")
