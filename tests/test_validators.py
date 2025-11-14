"""Custom validators for testing custom validator functionality."""

from django.core.exceptions import ValidationError


def validate_even_number(value: int) -> None:
    """
    Validate that the value is an even number.

    Args:
        value: The value to validate

    Raises:
        ValidationError: If the value is not an even number
    """
    if int(value) % 2 != 0:
        raise ValidationError(
            f"{value} n'est pas un nombre pair",
            code="not_even",
        )


class CustomRangeValidator:
    """
    Validator class that checks if value is within a specified range.

    This is a class-based validator that demonstrates how custom
    validators can accept parameters during instantiation.
    """

    def __init__(self, min_value: int = 0, max_value: int = 100):
        """
        Initialize the validator with min and max values.

        Args:
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)
        """
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, value: int) -> None:
        """
        Validate that value is within the range.

        Args:
            value: The value to validate

        Raises:
            ValidationError: If value is outside the range
        """
        int_value = int(value)
        if not (self.min_value <= int_value <= self.max_value):
            raise ValidationError(
                f"La valeur {int_value} doit être entre "
                f"{self.min_value} et {self.max_value}",
                code="out_of_range",
            )


def validate_positive(value: int) -> None:
    """
    Validate that the value is positive.

    Args:
        value: The value to validate

    Raises:
        ValidationError: If the value is not positive
    """
    if int(value) <= 0:
        raise ValidationError(
            f"{value} doit être un nombre positif",
            code="not_positive",
        )
