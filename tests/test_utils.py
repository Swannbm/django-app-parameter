"""Tests for utility functions in django_app_parameter.utils"""

import pytest

from django_app_parameter.models import parameter_slugify
from django_app_parameter.utils import (
    clear_validator_cache,
    get_available_validators,
    get_setting,
    get_validator_from_registry,
    import_validator,
)


class TestParameterSlugify:
    """Tests for parameter_slugify function"""

    def test_slugify_basic(self):
        """Test basic slugify with simple text"""
        assert parameter_slugify("hello world") == "HELLO_WORLD"

    def test_slugify_with_special_chars(self):
        """Test slugify with special characters"""
        assert parameter_slugify("hello@world#test") == "HELLOWORLDTEST"

    def test_slugify_with_spaces(self):
        """Test slugify with multiple spaces"""
        assert parameter_slugify("hello   world   test") == "HELLO_WORLD_TEST"

    def test_slugify_uppercase(self):
        """Test slugify with uppercase input"""
        assert parameter_slugify("HELLO WORLD") == "HELLO_WORLD"

    def test_slugify_mixed_case(self):
        """Test slugify with mixed case"""
        assert parameter_slugify("Hello World") == "HELLO_WORLD"

    def test_slugify_with_dashes(self):
        """Test slugify replaces dashes with underscores"""
        assert parameter_slugify("hello-world-test") == "HELLO_WORLD_TEST"

    def test_slugify_with_underscores(self):
        """Test slugify preserves underscores from original dashes"""
        assert parameter_slugify("test_name") == "TEST_NAME"

    def test_slugify_numbers(self):
        """Test slugify with numbers"""
        assert parameter_slugify("test 123") == "TEST_123"

    def test_slugify_accented_chars(self):
        """Test slugify with accented characters"""
        # Django's slugify converts accented chars to ASCII equivalents
        assert parameter_slugify("café") == "CAFE"
        assert parameter_slugify("naïve") == "NAIVE"

    def test_slugify_empty_string(self):
        """Test slugify with empty string"""
        assert parameter_slugify("") == ""

    def test_slugify_only_special_chars(self):
        """Test slugify with only special characters"""
        assert parameter_slugify("@#$%") == ""

    def test_slugify_from_readme_examples(self):
        """Test examples from README"""
        assert parameter_slugify("blog title") == "BLOG_TITLE"
        assert parameter_slugify("sender e-mail") == "SENDER_E_MAIL"
        # Note: Django's slugify removes special chars, so ##weird@Na_me becomes
        assert parameter_slugify("##weird@Na_me") == "WEIRDNA_ME"


class TestGetSetting:
    """Tests for get_setting utility function"""

    def test_get_setting_exists(self, settings):
        """Test getting an existing setting"""
        settings.DJANGO_APP_PARAMETER = {"validators": {"test": "path.to.test"}}
        result = get_setting("validators")
        assert result == {"test": "path.to.test"}

    def test_get_setting_missing_with_default(self, settings):
        """Test getting a missing setting with default value"""
        settings.DJANGO_APP_PARAMETER = {}
        result = get_setting("missing_key", {"default": "value"})
        assert result == {"default": "value"}

    def test_get_setting_missing_without_default(self, settings):
        """Test getting a missing setting without default"""
        settings.DJANGO_APP_PARAMETER = {}
        result = get_setting("missing_key")
        assert result is None

    def test_get_setting_no_django_app_parameter(self, settings):
        """Test when DJANGO_APP_PARAMETER setting doesn't exist"""
        if hasattr(settings, "DJANGO_APP_PARAMETER"):
            delattr(settings, "DJANGO_APP_PARAMETER")
        result = get_setting("any_key", "default")
        assert result == "default"


class TestImportValidator:
    """Tests for import_validator utility function"""

    def test_import_validator_function(self):
        """Test importing a function validator"""
        validator = import_validator("tests.test_validators.validate_even_number")
        assert callable(validator)
        assert validator.__name__ == "validate_even_number"

    def test_import_validator_class(self):
        """Test importing a class validator"""
        ValidatorClass = import_validator("tests.test_validators.CustomRangeValidator")
        assert callable(ValidatorClass)
        assert ValidatorClass.__name__ == "CustomRangeValidator"

    def test_import_validator_invalid_path_format(self):
        """Test importing with invalid path format (no dot)"""
        with pytest.raises(ImportError, match="Invalid validator path"):
            import_validator("invalid_path")

    def test_import_validator_nonexistent_module(self):
        """Test importing from nonexistent module"""
        with pytest.raises(ImportError, match="Cannot import module"):
            import_validator("nonexistent.module.validator")

    def test_import_validator_nonexistent_attribute(self):
        """Test importing nonexistent attribute from valid module"""
        with pytest.raises(AttributeError, match="does not have attribute"):
            import_validator("tests.test_validators.nonexistent_validator")


class TestGetValidatorFromRegistry:
    """Tests for get_validator_from_registry utility function"""

    def test_get_builtin_validator(self):
        """Test getting a built-in Django validator"""
        from django.core.validators import MinValueValidator

        validator = get_validator_from_registry("MinValueValidator")
        assert validator is MinValueValidator

    def test_get_custom_validator_from_settings(self, settings):
        """Test getting a custom validator from settings"""
        settings.DJANGO_APP_PARAMETER = {
            "validators": {"even_number": "tests.test_validators.validate_even_number"}
        }
        clear_validator_cache()

        validator = get_validator_from_registry("even_number")
        assert callable(validator)
        assert validator.__name__ == "validate_even_number"

    def test_get_validator_not_found(self, settings):
        """Test getting a validator that doesn't exist"""
        settings.DJANGO_APP_PARAMETER = {"validators": {}}
        clear_validator_cache()

        validator = get_validator_from_registry("nonexistent")
        assert validator is None

    def test_get_validator_caching(self, settings):
        """Test that validators are cached"""
        settings.DJANGO_APP_PARAMETER = {
            "validators": {"even_number": "tests.test_validators.validate_even_number"}
        }
        clear_validator_cache()

        # First call
        validator1 = get_validator_from_registry("even_number", use_cache=True)
        # Second call should return same object from cache
        validator2 = get_validator_from_registry("even_number", use_cache=True)

        assert validator1 is validator2

    def test_get_validator_no_cache(self, settings):
        """Test getting validator without cache"""
        settings.DJANGO_APP_PARAMETER = {
            "validators": {"even_number": "tests.test_validators.validate_even_number"}
        }
        clear_validator_cache()

        validator = get_validator_from_registry("even_number", use_cache=False)
        assert callable(validator)

    def test_builtin_validators_available(self):
        """Test that all built-in validators are available"""
        builtin_validators = [
            "MinValueValidator",
            "MaxValueValidator",
            "MinLengthValidator",
            "MaxLengthValidator",
            "RegexValidator",
            "EmailValidator",
            "URLValidator",
            "validate_slug",
            "validate_ipv4_address",
            "validate_ipv6_address",
            "FileExtensionValidator",
        ]

        for validator_name in builtin_validators:
            validator = get_validator_from_registry(validator_name)
            assert validator is not None

    def test_get_validator_import_error(self, settings):
        """Test get_validator_from_registry with ImportError"""
        settings.DJANGO_APP_PARAMETER = {
            "validators": {"broken_module": "nonexistent.module.validator_function"}
        }
        clear_validator_cache()

        with pytest.raises(ImportError, match="Cannot import module"):
            get_validator_from_registry("broken_module")

    def test_get_validator_attribute_error(self, settings):
        """Test get_validator_from_registry with AttributeError"""
        settings.DJANGO_APP_PARAMETER = {
            "validators": {"broken_attr": "tests.test_validators.nonexistent_function"}
        }
        clear_validator_cache()

        with pytest.raises(AttributeError, match="does not have attribute"):
            get_validator_from_registry("broken_attr")


class TestGetAvailableValidators:
    """Tests for get_available_validators utility function"""

    def test_get_available_validators_builtin_only(self, settings):
        """Test getting available validators with only built-in validators"""
        settings.DJANGO_APP_PARAMETER = {}
        validators = get_available_validators()

        # Should contain built-in validators
        assert "MinValueValidator" in validators
        assert "MaxValueValidator" in validators
        assert validators["MinValueValidator"] == "Valeur minimale"

    def test_get_available_validators_with_custom(self, settings):
        """Test getting available validators including custom ones"""
        settings.DJANGO_APP_PARAMETER = {
            "validators": {
                "even_number": "tests.test_validators.validate_even_number",
                "positive": "tests.test_validators.validate_positive",
            }
        }

        validators = get_available_validators()

        # Should contain built-in validators
        assert "MinValueValidator" in validators

        # Should contain custom validators
        assert "even_number" in validators
        assert "positive" in validators

        # Custom validators should have "(custom)" in display name
        assert "custom" in validators["even_number"].lower()
        assert "custom" in validators["positive"].lower()

    def test_get_available_validators_display_names(self):
        """Test that display names are user-friendly"""
        validators = get_available_validators()

        # Check French display names for built-in validators
        assert validators["MinValueValidator"] == "Valeur minimale"
        assert validators["MaxValueValidator"] == "Valeur maximale"
        assert validators["EmailValidator"] == "Validation email"
        assert validators["URLValidator"] == "Validation URL"

    def test_custom_validator_display_name_formatting(self, settings):
        """Test that custom validator display names are formatted nicely"""
        settings.DJANGO_APP_PARAMETER = {
            "validators": {"even_number_check": "tests.test_validators.validate_even"}
        }

        validators = get_available_validators()

        # Should convert underscores to spaces and title case
        display_name = validators["even_number_check"]
        assert "Even Number Check" in display_name
        assert "(custom)" in display_name.lower()


class TestClearValidatorCache:
    """Tests for clear_validator_cache utility function"""

    def test_clear_validator_cache(self, settings):
        """Test that clearing cache removes cached validators"""
        settings.DJANGO_APP_PARAMETER = {
            "validators": {"even_number": "tests.test_validators.validate_even_number"}
        }

        # Load validator to cache it
        get_validator_from_registry("even_number", use_cache=True)

        # Clear cache
        clear_validator_cache()

        # After clearing, validator should be re-imported
        # (we can't directly test cache state, but this ensures no errors)
        validator = get_validator_from_registry("even_number", use_cache=True)
        assert callable(validator)

    def test_clear_empty_cache(self):
        """Test clearing an empty cache doesn't raise errors"""
        clear_validator_cache()
        clear_validator_cache()  # Call twice to ensure it's safe
