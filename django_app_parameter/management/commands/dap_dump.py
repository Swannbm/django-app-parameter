"""Command to export parameters from the database to a JSON file

Arguments:
    file: path to the JSON file to create (required)
"""

import json
import logging
from typing import TYPE_CHECKING, Any

from django.core.management.base import BaseCommand, CommandParser

from django_app_parameter.models import Parameter

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Export parameters from the database to a JSON file"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "file",
            type=str,
            help="path to the JSON file to create",
        )
        parser.add_argument(
            "--indent",
            type=int,
            default=4,
            help="JSON indentation level (default: 4)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        logger.info("Dump parameter start")

        file_path: str = options["file"]
        indent: int = options["indent"]

        # Get all parameters as JSON
        if TYPE_CHECKING:
            manager = Parameter.objects
            data = manager.dump_to_json()
        else:
            data = Parameter.objects.dump_to_json()  # type: ignore[attr-defined]

        # Write to file
        logger.info("Writing to file %s", file_path)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully exported {len(data)} parameter(s) to {file_path}"
            )
        )
        logger.info("End dump parameter")
