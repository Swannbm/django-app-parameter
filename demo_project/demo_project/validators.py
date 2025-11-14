"""Custom validators for demo_project."""

from django.core.exceptions import ValidationError


def validate_business_hours(value: str) -> None:
    """
    Validate that the time is during business hours (9:00 - 18:00).

    Args:
        value: Time string in HH:MM:SS format

    Raises:
        ValidationError: If time is outside business hours
    """
    try:
        hour = int(value.split(":")[0])
    except (ValueError, IndexError) as e:
        raise ValidationError(f"Format invalide: {value}. Attendu: HH:MM:SS") from e

    if not (9 <= hour < 18):
        raise ValidationError(
            f"L'heure {value} doit être entre 09:00:00 et 17:59:59 (heures ouvrables)",
            code="outside_business_hours",
        )


class AgeValidator:
    """
    Validator class to check if age is valid (between min and max).

    This demonstrates a parameterized class-based validator.
    """

    def __init__(self, min_age: int = 18, max_age: int = 120):
        """
        Initialize with minimum and maximum age.

        Args:
            min_age: Minimum allowed age
            max_age: Maximum allowed age
        """
        self.min_age = min_age
        self.max_age = max_age

    def __call__(self, value: int) -> None:
        """
        Validate the age.

        Args:
            value: The age to validate

        Raises:
            ValidationError: If age is invalid
        """
        try:
            age = int(value)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Âge invalide: {value}") from e

        if not (self.min_age <= age <= self.max_age):
            raise ValidationError(
                f"L'âge doit être entre {self.min_age} et {self.max_age} ans. "
                f"Valeur fournie: {age}",
                code="invalid_age",
            )
