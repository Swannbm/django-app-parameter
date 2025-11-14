"""Command to import parameters into the database

Arguments:
    --file: a json file with all the parameter to be added
    --no-update: flag to avoid updating existing parameters
    --json: dict containing a new parameter's values, can't be use with --file
"""

import argparse
import json
import logging
from typing import TYPE_CHECKING, Any

from django.core.management.base import BaseCommand, CommandParser

from django_app_parameter.models import Parameter, ParameterValidator, parameter_slugify

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

    QuerySetPV = QuerySet[ParameterValidator]

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
        self.do_update = not options.get("no_update", False)
        if "file" in options:
            logger.info("Read file %s", options["file"])
            # required check to be compatible with call_command()
            if isinstance(options["file"], str):
                options["file"] = open(options["file"])
            json_data = json.loads(options["file"].read())
            self.load_json(json_data)
        elif "json" in options:
            # required check to be compatible with call_command()
            if isinstance(options["json"], str):
                options["json"] = json.loads(options["json"])
            self.load_json(options["json"])
        logger.info("End load parameter")

    def load_json(self, data: Any) -> None:
        logger.info("load json")
        for param_values in data:
            if "slug" in param_values:
                slug = param_values["slug"]
            else:
                slug = parameter_slugify(param_values["name"])

            # Extract validators from param_values if present
            validators_data = param_values.pop("validators", None)

            if self.do_update:
                logger.info("Updating parameter %s", slug)
                param, _ = Parameter.objects.update_or_create(
                    slug=slug, defaults=param_values
                )
            else:
                logger.info("Adding parameter %s (no update)", slug)
                param, _ = Parameter.objects.get_or_create(
                    slug=slug, defaults=param_values
                )

            # Handle validators - always process to ensure consistency
            self._handle_validators(param, validators_data)

    def _handle_validators(
        self, parameter: Parameter, validators_data: list[dict[str, Any]] | None
    ) -> None:
        """Handle creation/update of validators for a parameter.

        The validators in the JSON represent the desired final state.
        All existing validators are removed and replaced with the ones from JSON.
        If validators_data is None or empty, all validators are removed.

        Args:
            parameter: The Parameter instance to attach validators to
            validators_data: List of validator definitions from JSON, or None
        """
        # Always clear existing validators first to ensure consistency
        logger.info(
            "Clearing existing validators for parameter %s", parameter.slug
        )
        existing_parameters: QuerySetPV = parameter.validators.all()  # type: ignore[attr-defined]
        existing_parameters.delete()  # type: ignore[misc]

        # If no validators provided, we're done (validators are already cleared)
        if not validators_data:
            return

        # Create new validators from JSON
        for validator_data in validators_data:
            validator_type = validator_data.get("validator_type")
            validator_params = validator_data.get("validator_params", {})

            if not validator_type:
                logger.warning(
                    "Skipping validator without validator_type for parameter %s",
                    parameter.slug,
                )
                continue

            # Create validator
            logger.info(
                "Creating validator %s for parameter %s",
                validator_type,
                parameter.slug,
            )
            parameter.validators.create(  # type: ignore[attr-defined]
                validator_type=validator_type,
                validator_params=validator_params,
            )
