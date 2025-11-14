import json
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command

from django_app_parameter import app_parameter
from django_app_parameter.context_processors import add_global_parameter_context
from django_app_parameter.models import Parameter, ParameterValidator


@pytest.fixture
def params(db):
    params = [
        Parameter(
            name="blog title",
            value="my awesome blog",
            slug="BLOG_TITLE",
        ),
        Parameter(
            name="year of birth",
            slug="BIRTH_YEAR",
            value="1983",
            value_type=Parameter.TYPES.INT,
            is_global=True,
        ),
        Parameter(
            name="a small json",
            slug="SM_JSON",
            value="[1, 2, 3]",
            value_type=Parameter.TYPES.JSN,
        ),
    ]
    Parameter.objects.bulk_create(params)
    return params


class TestParameter:
    @pytest.mark.django_db
    def test_default_slug(self):
        param = Parameter(
            name="testing is good#",
            value="hello world",
        )
        param.save()
        assert param.slug == "TESTING_IS_GOOD"

    def test_default_str(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="hello world",
        )
        assert param.value_type == Parameter.TYPES.STR
        assert isinstance(param.get(), str)

    def test_str(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="1",
        )
        result = param.str()
        assert isinstance(result, str)
        assert result == "1"
        assert isinstance(param.get(), str)

    def test_int(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="1",
            value_type=Parameter.TYPES.INT,
        )
        result = param.int()
        assert isinstance(result, int)
        assert result == 1
        assert isinstance(param.get(), int)

    def test_float(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="0.1",
            value_type=Parameter.TYPES.FLT,
        )
        result = param.float()
        assert isinstance(result, float)
        assert result == 0.1
        assert isinstance(param.get(), float)

    def test_decimal(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="0.2",
            value_type=Parameter.TYPES.DCL,
        )
        result = param.decimal()
        assert isinstance(result, Decimal)
        assert result == Decimal("0.2")
        assert isinstance(param.get(), Decimal)

    def json(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="{'hello': ['world', 'testers']}",
            value_type=Parameter.TYPES.JSN,
        )
        result = param.json()
        assert isinstance(result, dict)
        assert result["hello"][1] == "testers"
        assert isinstance(param.get(), dict)

    def test_dundo_str(self):
        param = Parameter(
            name="testing",
            value="hello world",
        )
        assert str(param) == "testing"

    def test_bool(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="True",
            value_type=Parameter.TYPES.BOO,
        )
        result = param.bool()
        assert isinstance(result, bool)
        assert result is True
        assert isinstance(param.get(), bool)
        param.value = "False"  # type: ignore[assignment]
        assert param.bool() is False
        param.value = "0"  # type: ignore[assignment]
        assert param.bool() is False

    def test_date(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="2024-03-15",
            value_type=Parameter.TYPES.DATE,
        )
        result = param.date()
        assert isinstance(result, date)
        assert result == date(2024, 3, 15)
        assert isinstance(param.get(), date)

    def test_datetime(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="2024-03-15T14:30:00",
            value_type=Parameter.TYPES.DATETIME,
        )
        result = param.datetime()
        assert isinstance(result, datetime)
        assert result == datetime(2024, 3, 15, 14, 30, 0)
        assert isinstance(param.get(), datetime)

    def test_time(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="14:30:00",
            value_type=Parameter.TYPES.TIME,
        )
        result = param.time()
        assert isinstance(result, time)
        assert result == time(14, 30, 0)
        assert isinstance(param.get(), time)

    def test_url(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="https://example.com/api",
            value_type=Parameter.TYPES.URL,
        )
        result = param.url()
        assert isinstance(result, str)
        assert result == "https://example.com/api"
        assert isinstance(param.get(), str)

    def test_url_invalid(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="not-a-valid-url",
            value_type=Parameter.TYPES.URL,
        )
        with pytest.raises(ValueError, match="Invalid URL"):
            param.url()

    def test_email(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="admin@example.com",
            value_type=Parameter.TYPES.EMAIL,
        )
        result = param.email()
        assert isinstance(result, str)
        assert result == "admin@example.com"
        assert isinstance(param.get(), str)

    def test_email_invalid(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="not-an-email",
            value_type=Parameter.TYPES.EMAIL,
        )
        with pytest.raises(ValueError, match="Invalid email"):
            param.email()

    def test_list(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="item1, item2, item3",
            value_type=Parameter.TYPES.LIST,
        )
        result = param.list()
        assert isinstance(result, list)
        assert result == ["item1", "item2", "item3"]
        assert isinstance(param.get(), list)

    def test_list_empty(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="",
            value_type=Parameter.TYPES.LIST,
        )
        result = param.list()
        assert result == []

    def test_dict(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value='{"key": "value", "count": 42}',
            value_type=Parameter.TYPES.DICT,
        )
        result = param.dict()
        assert isinstance(result, dict)
        assert result == {"key": "value", "count": 42}
        assert isinstance(param.get(), dict)

    def test_dict_invalid_not_dict(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="[1, 2, 3]",
            value_type=Parameter.TYPES.DICT,
        )
        with pytest.raises(ValueError, match="Expected dict"):
            param.dict()

    def test_path(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="/media/uploads/documents",
            value_type=Parameter.TYPES.PATH,
        )
        result = param.path()
        assert isinstance(result, Path)
        assert result == Path("/media/uploads/documents")
        assert isinstance(param.get(), Path)

    def test_duration(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="3600",
            value_type=Parameter.TYPES.DURATION,
        )
        result = param.duration()
        assert isinstance(result, timedelta)
        assert result == timedelta(seconds=3600)
        assert isinstance(param.get(), timedelta)

    def test_duration_float(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="3600.5",
            value_type=Parameter.TYPES.DURATION,
        )
        result = param.duration()
        assert result == timedelta(seconds=3600.5)

    def test_percentage(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="75.5",
            value_type=Parameter.TYPES.PERCENTAGE,
        )
        result = param.percentage()
        assert isinstance(result, float)
        assert result == 75.5
        assert isinstance(param.get(), float)

    def test_percentage_invalid_too_high(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="150",
            value_type=Parameter.TYPES.PERCENTAGE,
        )
        with pytest.raises(ValueError, match="must be between 0 and 100"):
            param.percentage()

    def test_percentage_invalid_negative(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="-10",
            value_type=Parameter.TYPES.PERCENTAGE,
        )
        with pytest.raises(ValueError, match="must be between 0 and 100"):
            param.percentage()

    @pytest.mark.django_db
    def test_to_dict_basic(self):
        """Test to_dict() returns correct dictionary structure"""
        param = Parameter.objects.create(
            name="Test Param",
            slug="TEST_PARAM",
            value="test value",
            value_type=Parameter.TYPES.STR,
            description="Test description",
            is_global=True,
        )
        result = param.to_dict()

        assert isinstance(result, dict)
        assert result["name"] == "Test Param"
        assert result["slug"] == "TEST_PARAM"
        assert result["value"] == "test value"
        assert result["value_type"] == Parameter.TYPES.STR
        assert result["description"] == "Test description"
        assert result["is_global"] is True
        assert "validators" not in result

    @pytest.mark.django_db
    def test_to_dict_with_validators(self):
        """Test to_dict() includes validators"""
        param = Parameter.objects.create(
            name="Validated Param",
            slug="VALIDATED_PARAM",
            value="50",
            value_type=Parameter.TYPES.INT,
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="MinValueValidator",
            validator_params={"limit_value": 10},
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="MaxValueValidator",
            validator_params={"limit_value": 100},
        )

        result = param.to_dict()

        assert "validators" in result
        assert len(result["validators"]) == 2
        assert result["validators"][0]["validator_type"] == "MinValueValidator"
        assert result["validators"][0]["validator_params"] == {"limit_value": 10}
        assert result["validators"][1]["validator_type"] == "MaxValueValidator"
        assert result["validators"][1]["validator_params"] == {"limit_value": 100}

    @pytest.mark.django_db
    def test_to_dict_minimal(self):
        """Test to_dict() with minimal parameter (no description, not global)"""
        param = Parameter.objects.create(
            name="Minimal",
            slug="MINIMAL",
            value="value",
        )
        result = param.to_dict()

        assert result["name"] == "Minimal"
        assert result["slug"] == "MINIMAL"
        assert result["value"] == "value"
        assert result["value_type"] == Parameter.TYPES.STR  # default
        assert result["description"] == ""
        assert result["is_global"] is False
        assert "validators" not in result

    @pytest.mark.django_db
    def test_from_dict_create_new(self):
        """Test from_dict() creates a new parameter"""
        param = Parameter()
        data = {
            "name": "New Param",
            "slug": "NEW_PARAM",
            "value": "test value",
            "value_type": Parameter.TYPES.STR,
            "description": "Test description",
            "is_global": True,
        }
        param.from_dict(data)

        assert param.pk is not None  # Should be saved
        assert param.name == "New Param"
        assert param.slug == "NEW_PARAM"
        assert param.value == "test value"
        assert param.value_type == Parameter.TYPES.STR
        assert param.description == "Test description"
        assert param.is_global is True

    @pytest.mark.django_db
    def test_from_dict_update_existing(self):
        """Test from_dict() updates an existing parameter"""
        param = Parameter.objects.create(
            name="Original Name",
            slug="ORIGINAL_SLUG",
            value="original value",
            value_type=Parameter.TYPES.STR,
            description="Original description",
            is_global=False,
        )

        # Update with new data
        data = {
            "name": "Updated Name",
            "value": "updated value",
            "description": "Updated description",
            "is_global": True,
            # slug and value_type should be ignored for existing instances
            "slug": "NEW_SLUG",
            "value_type": Parameter.TYPES.INT,
        }
        param.from_dict(data)

        param.refresh_from_db()
        assert param.name == "Updated Name"
        assert param.value == "updated value"
        assert param.description == "Updated description"
        assert param.is_global is True
        # These should not change for existing instances
        assert param.slug == "ORIGINAL_SLUG"
        assert param.value_type == Parameter.TYPES.STR

    @pytest.mark.django_db
    def test_from_dict_with_validators(self):
        """Test from_dict() handles validators"""
        param = Parameter()
        data = {
            "name": "Validated Param",
            "slug": "VALIDATED_PARAM",
            "value": "50",
            "value_type": Parameter.TYPES.INT,
            "validators": [
                {
                    "validator_type": "MinValueValidator",
                    "validator_params": {"limit_value": 10},
                },
                {
                    "validator_type": "MaxValueValidator",
                    "validator_params": {"limit_value": 100},
                },
            ],
        }
        param.from_dict(data)

        assert param.validators.count() == 2
        validators = list(param.validators.all())
        assert validators[0].validator_type == "MinValueValidator"
        assert validators[0].validator_params == {"limit_value": 10}
        assert validators[1].validator_type == "MaxValueValidator"
        assert validators[1].validator_params == {"limit_value": 100}

    @pytest.mark.django_db
    def test_from_dict_replaces_validators(self):
        """Test from_dict() replaces existing validators"""
        param = Parameter.objects.create(
            name="Test Param",
            slug="TEST_PARAM",
            value="50",
            value_type=Parameter.TYPES.INT,
        )
        # Add initial validators
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="MinValueValidator",
            validator_params={"limit_value": 5},
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="MaxValueValidator",
            validator_params={"limit_value": 200},
        )

        assert param.validators.count() == 2

        # Update with new validators
        data = {
            "name": "Test Param",
            "value": "50",
            "validators": [
                {
                    "validator_type": "MinValueValidator",
                    "validator_params": {"limit_value": 10},
                }
            ],
        }
        param.from_dict(data)

        # Should have only the new validator
        assert param.validators.count() == 1
        validator = param.validators.first()
        assert validator.validator_type == "MinValueValidator"
        assert validator.validator_params == {"limit_value": 10}

    @pytest.mark.django_db
    def test_from_dict_clears_validators(self):
        """Test from_dict() can clear all validators"""
        param = Parameter.objects.create(
            name="Test Param",
            slug="TEST_PARAM",
            value="50",
            value_type=Parameter.TYPES.INT,
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="MinValueValidator",
            validator_params={"limit_value": 10},
        )

        assert param.validators.count() == 1

        # Update with empty validators list
        data = {
            "name": "Test Param",
            "value": "50",
            "validators": [],
        }
        param.from_dict(data)

        # Validators should be cleared
        assert param.validators.count() == 0

    @pytest.mark.django_db
    def test_from_dict_partial_update(self):
        """Test from_dict() with partial data"""
        param = Parameter.objects.create(
            name="Original",
            slug="ORIGINAL",
            value="original",
            description="original description",
            is_global=False,
        )

        # Update only name and value
        data = {
            "name": "Updated Name",
            "value": "updated value",
        }
        param.from_dict(data)

        param.refresh_from_db()
        assert param.name == "Updated Name"
        assert param.value == "updated value"
        # These should remain unchanged
        assert param.description == "original description"
        assert param.is_global is False


@pytest.mark.django_db
class TestParameterManager:
    def test_fixtures(self, params):
        assert Parameter.objects.all().count() == 3

    def test_get_from_slug(self, params):
        params = Parameter.objects.get_from_slug("BIRTH_YEAR")
        assert params.int() == 1983
        with pytest.raises(ImproperlyConfigured):
            Parameter.objects.get_from_slug("NOT_EXISTING")

    def test_access(self, params):
        assert Parameter.objects.int("BIRTH_YEAR") == 1983
        assert Parameter.objects.str("BIRTH_YEAR") == "1983"
        assert Parameter.objects.float("BIRTH_YEAR") == float("1983")
        assert Parameter.objects.decimal("BIRTH_YEAR") == Decimal("1983")
        assert Parameter.objects.float("BIRTH_YEAR") == float("1983")
        assert Parameter.objects.json("SM_JSON") == [1, 2, 3]

    def test_manager_bool(self):
        """Test Parameter.objects.bool() manager method"""
        Parameter.objects.create(
            name="Test Bool",
            slug="TEST_BOOL",
            value="1",
            value_type=Parameter.TYPES.BOO,
        )
        result = Parameter.objects.bool("TEST_BOOL")
        assert result is True
        assert isinstance(result, bool)

    def test_manager_date(self):
        """Test Parameter.objects.date() manager method"""
        Parameter.objects.create(
            name="Test Date",
            slug="TEST_DATE",
            value="2024-01-15",
            value_type=Parameter.TYPES.DATE,
        )
        result = Parameter.objects.date("TEST_DATE")
        assert result == date(2024, 1, 15)
        assert isinstance(result, date)

    def test_manager_datetime(self):
        """Test Parameter.objects.datetime() manager method"""
        Parameter.objects.create(
            name="Test DateTime",
            slug="TEST_DATETIME",
            value="2024-01-15T10:30:00",
            value_type=Parameter.TYPES.DATETIME,
        )
        result = Parameter.objects.datetime("TEST_DATETIME")
        assert result == datetime(2024, 1, 15, 10, 30, 0)
        assert isinstance(result, datetime)

    def test_manager_time(self):
        """Test Parameter.objects.time() manager method"""
        Parameter.objects.create(
            name="Test Time",
            slug="TEST_TIME",
            value="14:30:00",
            value_type=Parameter.TYPES.TIME,
        )
        result = Parameter.objects.time("TEST_TIME")
        assert result == time(14, 30, 0)
        assert isinstance(result, time)

    def test_manager_url(self):
        """Test Parameter.objects.url() manager method"""
        Parameter.objects.create(
            name="Test URL",
            slug="TEST_URL",
            value="https://example.com",
            value_type=Parameter.TYPES.URL,
        )
        result = Parameter.objects.url("TEST_URL")
        assert result == "https://example.com"
        assert isinstance(result, str)

    def test_manager_email(self):
        """Test Parameter.objects.email() manager method"""
        Parameter.objects.create(
            name="Test Email",
            slug="TEST_EMAIL",
            value="test@example.com",
            value_type=Parameter.TYPES.EMAIL,
        )
        result = Parameter.objects.email("TEST_EMAIL")
        assert result == "test@example.com"
        assert isinstance(result, str)

    def test_manager_list(self):
        """Test Parameter.objects.list() manager method"""
        Parameter.objects.create(
            name="Test List",
            slug="TEST_LIST",
            value="a, b, c",
            value_type=Parameter.TYPES.LIST,
        )
        result = Parameter.objects.list("TEST_LIST")
        assert result == ["a", "b", "c"]
        assert isinstance(result, list)

    def test_manager_dict(self):
        """Test Parameter.objects.dict() manager method"""
        Parameter.objects.create(
            name="Test Dict",
            slug="TEST_DICT",
            value='{"key": "value"}',
            value_type=Parameter.TYPES.DICT,
        )
        result = Parameter.objects.dict("TEST_DICT")
        assert result == {"key": "value"}
        assert isinstance(result, dict)

    def test_manager_path(self):
        """Test Parameter.objects.path() manager method"""
        Parameter.objects.create(
            name="Test Path",
            slug="TEST_PATH",
            value="/tmp/test.txt",
            value_type=Parameter.TYPES.PATH,
        )
        result = Parameter.objects.path("TEST_PATH")
        assert result == Path("/tmp/test.txt")
        assert isinstance(result, Path)

    def test_manager_duration(self):
        """Test Parameter.objects.duration() manager method"""
        Parameter.objects.create(
            name="Test Duration",
            slug="TEST_DURATION",
            value="3600",
            value_type=Parameter.TYPES.DURATION,
        )
        result = Parameter.objects.duration("TEST_DURATION")
        assert result == timedelta(seconds=3600)
        assert isinstance(result, timedelta)

    def test_manager_percentage(self):
        """Test Parameter.objects.percentage() manager method"""
        Parameter.objects.create(
            name="Test Percentage",
            slug="TEST_PERCENTAGE",
            value="75.5",
            value_type=Parameter.TYPES.PERCENTAGE,
        )
        result = Parameter.objects.percentage("TEST_PERCENTAGE")
        assert result == 75.5
        assert isinstance(result, float)


@pytest.mark.django_db
class TestLoadParamMC:
    def test_json_options(self):
        data = json.dumps(
            [
                {
                    "name": "hello ze world",
                    "value": "yes",
                    "description": "123",
                    "is_global": True,
                },
                {
                    "slug": "A8B8C",
                    "name": "back on test",
                    "value": "yes",
                    "value_type": Parameter.TYPES.INT,
                },
            ]
        )
        call_command("load_param", json=data)
        param1 = Parameter.objects.get(slug="HELLO_ZE_WORLD")
        assert param1.str() == "yes"
        assert param1.name == "hello ze world"
        assert param1.is_global is True
        assert param1.description == "123"
        param2 = Parameter.objects.get(slug="A8B8C")
        assert param2.name == "back on test"
        assert param2.value_type == Parameter.TYPES.INT

    def test_file_options(self):
        call_command("load_param", file="django_app_parameter/data_for_test.json")
        param1 = Parameter.objects.get(slug="HELLO_ZE_WORLD")
        assert param1.str() == "yes"
        assert param1.name == "hello ze world"
        assert param1.is_global is True
        assert param1.description == "123"
        param2 = Parameter.objects.get(slug="A8B8C")
        assert param2.name == "back on test"
        assert param2.value_type == Parameter.TYPES.INT

    def test_noupdate_options(self, params):
        kwargs = {
            "json": json.dumps(
                [
                    {
                        "slug": "BIRTH_YEAR",
                        "name": "new name",
                        "value": "1982",
                    },
                    {
                        "name": "created",
                        "value": "true",
                    },
                ]
            ),
            "no_update": True,
        }
        call_command("load_param", **kwargs)
        assert app_parameter.BIRTH_YEAR == 1983
        assert Parameter.objects.filter(name="new name").exists() is False
        assert app_parameter.CREATED == "true"


@pytest.fixture
def custom_validators_settings(settings):
    """Configure custom validators for tests"""
    settings.DJANGO_APP_PARAMETER = {
        "validators": {
            "even_number": "tests.test_validators.validate_even_number",
            "custom_range": "tests.test_validators.CustomRangeValidator",
            "positive": "tests.test_validators.validate_positive",
        }
    }


@pytest.mark.django_db
class TestLoadParamWithValidators:
    """Test load_param management command with validators"""

    def test_load_param_with_single_validator(self):
        """Test loading a parameter with a single validator"""
        data = json.dumps(
            [
                {
                    "name": "Max Items",
                    "value": "50",
                    "value_type": Parameter.TYPES.INT,
                    "validators": [
                        {
                            "validator_type": "MinValueValidator",
                            "validator_params": {"limit_value": 10},
                        }
                    ],
                }
            ]
        )
        call_command("load_param", json=data)

        param = Parameter.objects.get(slug="MAX_ITEMS")
        assert param.validators.count() == 1

        validator = param.validators.first()
        assert validator.validator_type == "MinValueValidator"
        assert validator.validator_params == {"limit_value": 10}

    def test_load_param_with_multiple_validators(self):
        """Test loading a parameter with multiple validators"""
        data = json.dumps(
            [
                {
                    "name": "User Age",
                    "value": "25",
                    "value_type": Parameter.TYPES.INT,
                    "validators": [
                        {
                            "validator_type": "MinValueValidator",
                            "validator_params": {"limit_value": 18},
                        },
                        {
                            "validator_type": "MaxValueValidator",
                            "validator_params": {"limit_value": 120},
                        },
                    ],
                }
            ]
        )
        call_command("load_param", json=data)

        param = Parameter.objects.get(slug="USER_AGE")
        assert param.validators.count() == 2

        validator_types = list(
            param.validators.values_list("validator_type", flat=True)
        )
        assert "MinValueValidator" in validator_types
        assert "MaxValueValidator" in validator_types

    def test_load_param_with_custom_validator(self, custom_validators_settings):
        """Test loading a parameter with a custom validator from settings"""
        data = json.dumps(
            [
                {
                    "name": "Even Number",
                    "value": "10",
                    "value_type": Parameter.TYPES.INT,
                    "validators": [
                        {
                            "validator_type": "even_number",
                            "validator_params": {},
                        }
                    ],
                }
            ]
        )
        call_command("load_param", json=data)

        param = Parameter.objects.get(slug="EVEN_NUMBER")
        assert param.validators.count() == 1

        validator = param.validators.first()
        assert validator.validator_type == "even_number"

        # Test that the validator actually works
        from django.core.exceptions import ValidationError

        validator_func = validator.get_validator()
        validator_func(10)  # Should pass
        with pytest.raises(ValidationError):
            validator_func(11)  # Should fail

    def test_load_param_without_validators(self):
        """Test loading a parameter without validators (backwards compatibility)"""
        data = json.dumps(
            [
                {
                    "name": "Simple Param",
                    "value": "test",
                    "value_type": Parameter.TYPES.STR,
                }
            ]
        )
        call_command("load_param", json=data)

        param = Parameter.objects.get(slug="SIMPLE_PARAM")
        assert param.validators.count() == 0

    def test_load_param_with_empty_validators_list(self):
        """Test loading a parameter with an empty validators list"""
        data = json.dumps(
            [
                {
                    "name": "Empty Validators",
                    "value": "test",
                    "value_type": Parameter.TYPES.STR,
                    "validators": [],
                }
            ]
        )
        call_command("load_param", json=data)

        param = Parameter.objects.get(slug="EMPTY_VALIDATORS")
        assert param.validators.count() == 0

    def test_load_param_replaces_validators(self):
        """Test that validators are replaced (not updated) when parameter is reloaded"""
        # First load with two validators
        data1 = json.dumps(
            [
                {
                    "name": "Max Size",
                    "value": "100",
                    "value_type": Parameter.TYPES.INT,
                    "validators": [
                        {
                            "validator_type": "MinValueValidator",
                            "validator_params": {"limit_value": 10},
                        },
                        {
                            "validator_type": "MaxValueValidator",
                            "validator_params": {"limit_value": 100},
                        },
                    ],
                }
            ]
        )
        call_command("load_param", json=data1)

        param = Parameter.objects.get(slug="MAX_SIZE")
        assert param.validators.count() == 2

        # Second load with different validator (should replace all)
        data2 = json.dumps(
            [
                {
                    "name": "Max Size",
                    "value": "200",
                    "value_type": Parameter.TYPES.INT,
                    "validators": [
                        {
                            "validator_type": "MaxValueValidator",
                            "validator_params": {"limit_value": 200},
                        }
                    ],
                }
            ]
        )
        call_command("load_param", json=data2)

        param.refresh_from_db()
        # Should have only the new validator
        assert param.validators.count() == 1
        validator = param.validators.first()
        assert validator.validator_type == "MaxValueValidator"
        assert validator.validator_params == {"limit_value": 200}

    def test_load_param_removes_validators_when_not_in_json(self):
        """Test that validators are removed if not present in JSON"""
        # First load with validators
        data1 = json.dumps(
            [
                {
                    "name": "With Validators",
                    "value": "50",
                    "value_type": Parameter.TYPES.INT,
                    "validators": [
                        {
                            "validator_type": "MinValueValidator",
                            "validator_params": {"limit_value": 10},
                        }
                    ],
                }
            ]
        )
        call_command("load_param", json=data1)

        param = Parameter.objects.get(slug="WITH_VALIDATORS")
        assert param.validators.count() == 1

        # Second load without validators - should remove them
        data2 = json.dumps(
            [
                {
                    "name": "With Validators",
                    "value": "100",
                    "value_type": Parameter.TYPES.INT,
                }
            ]
        )
        call_command("load_param", json=data2)

        param.refresh_from_db()
        # Validators should be removed
        assert param.validators.count() == 0

    def test_load_param_validator_without_params(self):
        """Test loading a validator with no parameters (empty dict)"""
        data = json.dumps(
            [
                {
                    "name": "Email Field",
                    "value": "test@example.com",
                    "value_type": Parameter.TYPES.STR,
                    "validators": [
                        {
                            "validator_type": "EmailValidator",
                            "validator_params": {},
                        }
                    ],
                }
            ]
        )
        call_command("load_param", json=data)

        param = Parameter.objects.get(slug="EMAIL_FIELD")
        assert param.validators.count() == 1

        validator = param.validators.first()
        assert validator.validator_type == "EmailValidator"
        assert validator.validator_params == {}

    def test_load_param_skip_validator_without_type(self):
        """Test that validators without validator_type are skipped"""
        data = json.dumps(
            [
                {
                    "name": "Bad Validator",
                    "value": "50",
                    "value_type": Parameter.TYPES.INT,
                    "validators": [
                        {
                            "validator_params": {"limit_value": 10},
                        }
                    ],
                }
            ]
        )
        call_command("load_param", json=data)

        param = Parameter.objects.get(slug="BAD_VALIDATOR")
        # Should create parameter but skip invalid validator
        assert param.validators.count() == 0

    def test_load_param_add_validators_to_existing_param(self):
        """Test adding validators to an existing parameter that had none"""
        # First create parameter without validators
        data1 = json.dumps(
            [
                {
                    "name": "Growing Param",
                    "value": "100",
                    "value_type": Parameter.TYPES.INT,
                }
            ]
        )
        call_command("load_param", json=data1)

        param = Parameter.objects.get(slug="GROWING_PARAM")
        assert param.validators.count() == 0

        # Second load adds validators
        data2 = json.dumps(
            [
                {
                    "name": "Growing Param",
                    "value": "100",
                    "value_type": Parameter.TYPES.INT,
                    "validators": [
                        {
                            "validator_type": "MinValueValidator",
                            "validator_params": {"limit_value": 50},
                        }
                    ],
                }
            ]
        )
        call_command("load_param", json=data2)

        param.refresh_from_db()
        assert param.validators.count() == 1


@pytest.mark.django_db
class Test_app_parameter:
    def test_read_param(self, params):
        assert isinstance(app_parameter.BIRTH_YEAR, int)
        assert app_parameter.BIRTH_YEAR == 1983
        assert app_parameter.BLOG_TITLE == "my awesome blog"

    def test_set_param(self, params):
        with pytest.raises(Exception, match="You can't set an app parameter"):
            app_parameter.BIRTH_YEAR = 1983


@pytest.mark.django_db
class TestContextProcessor:
    def test_context(self, params):
        context = add_global_parameter_context(None)
        assert len(context) == 1
        assert "BIRTH_YEAR" in context


@pytest.mark.django_db
class TestParameterSetters:
    """Test all setter methods for Parameter model"""

    def test_set_int(self):
        param = Parameter.objects.create(
            name="test_int",
            value="0",
            value_type=Parameter.TYPES.INT,
        )
        param.set_int(42)
        param.refresh_from_db()
        assert param.value == "42"
        assert param.int() == 42

    def test_set_int_invalid_type(self):
        param = Parameter.objects.create(
            name="test_int",
            value="0",
            value_type=Parameter.TYPES.INT,
        )
        with pytest.raises(TypeError, match="Expected int"):
            param.set_int("not_an_int")

    def test_set_str(self):
        param = Parameter.objects.create(
            name="test_str",
            value="old",
            value_type=Parameter.TYPES.STR,
        )
        param.set_str("new value")
        param.refresh_from_db()
        assert param.value == "new value"
        assert param.str() == "new value"

    def test_set_str_invalid_type(self):
        param = Parameter.objects.create(
            name="test_str",
            value="old",
            value_type=Parameter.TYPES.STR,
        )
        with pytest.raises(TypeError, match="Expected str"):
            param.set_str(123)

    def test_set_float(self):
        param = Parameter.objects.create(
            name="test_float",
            value="0.0",
            value_type=Parameter.TYPES.FLT,
        )
        param.set_float(3.14)
        param.refresh_from_db()
        assert param.value == "3.14"
        assert param.float() == 3.14

    def test_set_float_invalid_type(self):
        param = Parameter.objects.create(
            name="test_float",
            value="0.0",
            value_type=Parameter.TYPES.FLT,
        )
        with pytest.raises(TypeError, match="Expected float"):
            param.set_float("not_a_float")

    def test_set_decimal(self):
        param = Parameter.objects.create(
            name="test_decimal",
            value="0.0",
            value_type=Parameter.TYPES.DCL,
        )
        param.set_decimal(Decimal("99.99"))
        param.refresh_from_db()
        assert param.value == "99.99"
        assert param.decimal() == Decimal("99.99")

    def test_set_bool(self):
        param = Parameter.objects.create(
            name="test_bool",
            value="0",
            value_type=Parameter.TYPES.BOO,
        )
        param.set_bool(True)
        param.refresh_from_db()
        assert param.value == "1"
        assert param.bool() is True

        param.set_bool(False)
        param.refresh_from_db()
        assert param.value == "0"
        assert param.bool() is False

    def test_set_date(self):
        param = Parameter.objects.create(
            name="test_date",
            value="2024-01-01",
            value_type=Parameter.TYPES.DATE,
        )
        new_date = date(2025, 12, 31)
        param.set_date(new_date)
        param.refresh_from_db()
        assert param.value == "2025-12-31"
        assert param.date() == new_date

    def test_set_datetime(self):
        param = Parameter.objects.create(
            name="test_datetime",
            value="2024-01-01T00:00:00",
            value_type=Parameter.TYPES.DATETIME,
        )
        new_dt = datetime(2025, 12, 31, 23, 59, 59)
        param.set_datetime(new_dt)
        param.refresh_from_db()
        assert param.value == "2025-12-31T23:59:59"
        assert param.datetime() == new_dt

    def test_set_time(self):
        param = Parameter.objects.create(
            name="test_time",
            value="00:00:00",
            value_type=Parameter.TYPES.TIME,
        )
        new_time = time(14, 30, 45)
        param.set_time(new_time)
        param.refresh_from_db()
        assert param.value == "14:30:45"
        assert param.time() == new_time

    def test_set_url(self):
        param = Parameter.objects.create(
            name="test_url",
            value="https://old.com",
            value_type=Parameter.TYPES.URL,
        )
        param.set_url("https://new.example.com")
        param.refresh_from_db()
        assert param.value == "https://new.example.com"
        assert param.url() == "https://new.example.com"

    def test_set_url_invalid(self):
        param = Parameter.objects.create(
            name="test_url",
            value="https://old.com",
            value_type=Parameter.TYPES.URL,
        )
        with pytest.raises(ValueError, match="Invalid URL"):
            param.set_url("not-a-valid-url")

    def test_set_email(self):
        param = Parameter.objects.create(
            name="test_email",
            value="old@example.com",
            value_type=Parameter.TYPES.EMAIL,
        )
        param.set_email("new@example.com")
        param.refresh_from_db()
        assert param.value == "new@example.com"
        assert param.email() == "new@example.com"

    def test_set_email_invalid(self):
        param = Parameter.objects.create(
            name="test_email",
            value="old@example.com",
            value_type=Parameter.TYPES.EMAIL,
        )
        with pytest.raises(ValueError, match="Invalid email"):
            param.set_email("not-an-email")

    def test_set_list(self):
        param = Parameter.objects.create(
            name="test_list",
            value="a, b, c",
            value_type=Parameter.TYPES.LIST,
        )
        param.set_list(["x", "y", "z"])
        param.refresh_from_db()
        assert param.value == "x, y, z"
        assert param.list() == ["x", "y", "z"]

    def test_set_list_empty(self):
        param = Parameter.objects.create(
            name="test_list",
            value="a, b",
            value_type=Parameter.TYPES.LIST,
        )
        param.set_list([])
        param.refresh_from_db()
        assert param.value == ""
        assert param.list() == []

    def test_set_dict(self):
        param = Parameter.objects.create(
            name="test_dict",
            value='{"old": "value"}',
            value_type=Parameter.TYPES.DICT,
        )
        param.set_dict({"new": "data", "count": 42})
        param.refresh_from_db()
        result = param.dict()
        assert result == {"new": "data", "count": 42}

    def test_set_path(self):
        param = Parameter.objects.create(
            name="test_path",
            value="/old/path",
            value_type=Parameter.TYPES.PATH,
        )
        param.set_path(Path("/new/path/to/file"))
        param.refresh_from_db()
        assert param.value == "/new/path/to/file"
        assert param.path() == Path("/new/path/to/file")

    def test_set_duration(self):
        param = Parameter.objects.create(
            name="test_duration",
            value="3600",
            value_type=Parameter.TYPES.DURATION,
        )
        param.set_duration(timedelta(hours=2))
        param.refresh_from_db()
        assert param.value == "7200.0"
        assert param.duration() == timedelta(hours=2)

    def test_set_percentage(self):
        param = Parameter.objects.create(
            name="test_percentage",
            value="50",
            value_type=Parameter.TYPES.PERCENTAGE,
        )
        param.set_percentage(75.5)
        param.refresh_from_db()
        assert param.value == "75.5"
        assert param.percentage() == 75.5

    def test_set_percentage_invalid_too_high(self):
        param = Parameter.objects.create(
            name="test_percentage",
            value="50",
            value_type=Parameter.TYPES.PERCENTAGE,
        )
        with pytest.raises(ValueError, match="must be between 0 and 100"):
            param.set_percentage(150)

    def test_set_percentage_invalid_negative(self):
        param = Parameter.objects.create(
            name="test_percentage",
            value="50",
            value_type=Parameter.TYPES.PERCENTAGE,
        )
        with pytest.raises(ValueError, match="must be between 0 and 100"):
            param.set_percentage(-10)

    def test_set_generic_int(self):
        """Test generic set() method with INT type"""
        param = Parameter.objects.create(
            name="test_generic",
            value="0",
            value_type=Parameter.TYPES.INT,
        )
        param.set(999)
        param.refresh_from_db()
        assert param.int() == 999

    def test_set_generic_str(self):
        """Test generic set() method with STR type"""
        param = Parameter.objects.create(
            name="test_generic",
            value="old",
            value_type=Parameter.TYPES.STR,
        )
        param.set("new string")
        param.refresh_from_db()
        assert param.str() == "new string"

    def test_set_generic_bool(self):
        """Test generic set() method with BOOL type"""
        param = Parameter.objects.create(
            name="test_generic",
            value="0",
            value_type=Parameter.TYPES.BOO,
        )
        param.set(True)
        param.refresh_from_db()
        assert param.bool() is True

    def test_set_json(self):
        """Test set_json with complex objects"""
        param = Parameter.objects.create(
            name="test_json",
            value="{}",
            value_type=Parameter.TYPES.JSN,
        )
        data = {"users": [{"name": "Alice"}, {"name": "Bob"}], "count": 2}
        param.set_json(data)
        param.refresh_from_db()
        assert param.json() == data

    def test_set_decimal_invalid_type(self):
        """Test set_decimal with invalid type"""
        param = Parameter.objects.create(
            name="test_decimal",
            value="0.0",
            value_type=Parameter.TYPES.DCL,
        )
        with pytest.raises(TypeError, match="Expected Decimal"):
            param.set_decimal(99.99)  # float instead of Decimal

    def test_set_bool_invalid_type(self):
        """Test set_bool with invalid type"""
        param = Parameter.objects.create(
            name="test_bool",
            value="0",
            value_type=Parameter.TYPES.BOO,
        )
        with pytest.raises(TypeError, match="Expected bool"):
            param.set_bool("true")  # string instead of bool

    def test_set_date_invalid_type(self):
        """Test set_date with invalid type"""
        param = Parameter.objects.create(
            name="test_date",
            value="2024-01-01",
            value_type=Parameter.TYPES.DATE,
        )
        with pytest.raises(TypeError, match="Expected date"):
            param.set_date("2024-01-01")  # string instead of date

    def test_set_datetime_invalid_type(self):
        """Test set_datetime with invalid type"""
        param = Parameter.objects.create(
            name="test_datetime",
            value="2024-01-01T00:00:00",
            value_type=Parameter.TYPES.DATETIME,
        )
        with pytest.raises(TypeError, match="Expected datetime"):
            param.set_datetime("2024-01-01T00:00:00")  # string instead of datetime

    def test_set_time_invalid_type(self):
        """Test set_time with invalid type"""
        param = Parameter.objects.create(
            name="test_time",
            value="00:00:00",
            value_type=Parameter.TYPES.TIME,
        )
        with pytest.raises(TypeError, match="Expected time"):
            param.set_time("14:30:00")  # string instead of time

    def test_set_url_invalid_type(self):
        """Test set_url with invalid type"""
        param = Parameter.objects.create(
            name="test_url",
            value="https://old.com",
            value_type=Parameter.TYPES.URL,
        )
        with pytest.raises(TypeError, match="Expected str"):
            param.set_url(123)  # int instead of str

    def test_set_email_invalid_type(self):
        """Test set_email with invalid type"""
        param = Parameter.objects.create(
            name="test_email",
            value="old@example.com",
            value_type=Parameter.TYPES.EMAIL,
        )
        with pytest.raises(TypeError, match="Expected str"):
            param.set_email(["not", "an", "email"])  # list instead of str

    def test_set_list_invalid_type(self):
        """Test set_list with invalid type"""
        param = Parameter.objects.create(
            name="test_list",
            value="a, b, c",
            value_type=Parameter.TYPES.LIST,
        )
        with pytest.raises(TypeError, match="Expected list"):
            param.set_list("a, b, c")  # string instead of list

    def test_set_dict_invalid_type(self):
        """Test set_dict with invalid type"""
        param = Parameter.objects.create(
            name="test_dict",
            value='{"old": "value"}',
            value_type=Parameter.TYPES.DICT,
        )
        with pytest.raises(TypeError, match="Expected dict"):
            param.set_dict("not a dict")  # string instead of dict

    def test_set_path_invalid_type(self):
        """Test set_path with invalid type"""
        param = Parameter.objects.create(
            name="test_path",
            value="/old/path",
            value_type=Parameter.TYPES.PATH,
        )
        with pytest.raises(TypeError, match="Expected Path"):
            param.set_path("/new/path")  # string instead of Path

    def test_set_duration_invalid_type(self):
        """Test set_duration with invalid type"""
        param = Parameter.objects.create(
            name="test_duration",
            value="3600",
            value_type=Parameter.TYPES.DURATION,
        )
        with pytest.raises(TypeError, match="Expected timedelta"):
            param.set_duration(3600)  # int instead of timedelta

    def test_set_percentage_invalid_type(self):
        """Test set_percentage with invalid type"""
        param = Parameter.objects.create(
            name="test_percentage",
            value="50",
            value_type=Parameter.TYPES.PERCENTAGE,
        )
        with pytest.raises(TypeError, match="Expected float or int"):
            param.set_percentage("75.5")  # string instead of float/int


@pytest.mark.django_db
class TestParameterValidator:
    """Test ParameterValidator model and validation logic"""

    def test_create_validator(self):
        param = Parameter.objects.create(
            name="test_age",
            value="25",
            value_type=Parameter.TYPES.INT,
        )
        validator = ParameterValidator.objects.create(
            parameter=param,
            validator_type="MinValueValidator",
            validator_params={"limit_value": 18},
        )
        assert validator.parameter == param
        assert validator.validator_type == "MinValueValidator"

    def test_validator_min_value(self):
        param = Parameter.objects.create(
            name="test_age",
            value="25",
            value_type=Parameter.TYPES.INT,
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="MinValueValidator",
            validator_params={"limit_value": 18},
        )
        # Should work
        param.set(30)
        assert param.int() == 30

        # Should fail
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            param.set(10)

    def test_validator_max_value(self):
        param = Parameter.objects.create(
            name="test_age",
            value="25",
            value_type=Parameter.TYPES.INT,
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="MaxValueValidator",
            validator_params={"limit_value": 100},
        )
        # Should work
        param.set(50)
        assert param.int() == 50

        # Should fail
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            param.set(150)

    def test_validator_multiple(self):
        """Test multiple validators on same parameter"""
        param = Parameter.objects.create(
            name="test_score",
            value="50",
            value_type=Parameter.TYPES.INT,
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="MinValueValidator",
            validator_params={"limit_value": 0},
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="MaxValueValidator",
            validator_params={"limit_value": 100},
        )

        # Should work
        param.set(75)
        assert param.int() == 75

        # Should fail - too low
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            param.set(-10)

        # Should fail - too high
        with pytest.raises(ValidationError):
            param.set(150)

    def test_validator_min_length(self):
        param = Parameter.objects.create(
            name="test_username",
            value="john",
            value_type=Parameter.TYPES.STR,
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="MinLengthValidator",
            validator_params={"limit_value": 3},
        )

        # Should work
        param.set("alice")
        assert param.str() == "alice"

        # Should fail
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            param.set("ab")

    def test_validator_max_length(self):
        param = Parameter.objects.create(
            name="test_code",
            value="ABC",
            value_type=Parameter.TYPES.STR,
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="MaxLengthValidator",
            validator_params={"limit_value": 10},
        )

        # Should work
        param.set("SHORT")
        assert param.str() == "SHORT"

        # Should fail
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            param.set("VERYLONGSTRING")

    def test_validator_regex(self):
        param = Parameter.objects.create(
            name="test_pattern",
            value="ABC123",
            value_type=Parameter.TYPES.STR,
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="RegexValidator",
            validator_params={"regex": r"^[A-Z]{3}\d{3}$"},
        )

        # Should work
        param.set("XYZ789")
        assert param.str() == "XYZ789"

        # Should fail
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            param.set("invalid")

    def test_get_validator_instance(self):
        """Test get_validator() returns correct validator instance"""
        param = Parameter.objects.create(
            name="test",
            value="10",
            value_type=Parameter.TYPES.INT,
        )
        param_validator = ParameterValidator.objects.create(
            parameter=param,
            validator_type="MinValueValidator",
            validator_params={"limit_value": 5},
        )

        validator = param_validator.get_validator()
        assert callable(validator)

        # Test it works
        validator(10)  # Should not raise

        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            validator(3)  # Should raise

    def test_validator_str_representation(self):
        param = Parameter.objects.create(
            name="test_param",
            value="10",
            value_type=Parameter.TYPES.INT,
        )
        validator = ParameterValidator.objects.create(
            parameter=param,
            validator_type="MinValueValidator",
            validator_params={"limit_value": 5},
        )
        assert str(validator) == "test_param - Valeur minimale"


@pytest.mark.django_db
class TestCustomValidators:
    """Test custom validators from settings"""

    def test_custom_function_validator_from_settings(self, custom_validators_settings):
        """Test using a custom function validator defined in settings"""
        param = Parameter.objects.create(
            name="test_even",
            value="4",
            value_type=Parameter.TYPES.INT,
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="even_number",  # From settings
        )

        # Should work with even numbers
        param.set(6)
        assert param.int() == 6

        # Should fail with odd numbers
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            param.set(7)

    def test_custom_class_validator_from_settings(self, custom_validators_settings):
        """Test using a custom class validator defined in settings"""
        param = Parameter.objects.create(
            name="test_range",
            value="50",
            value_type=Parameter.TYPES.INT,
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="custom_range",  # From settings
            validator_params={"min_value": 10, "max_value": 100},
        )

        # Should work within range
        param.set(75)
        assert param.int() == 75

        # Should fail outside range
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            param.set(5)  # Too low

        with pytest.raises(ValidationError):
            param.set(150)  # Too high

    def test_get_available_validators_includes_custom(self, custom_validators_settings):
        """Test that get_available_validators includes custom validators"""
        from django_app_parameter.utils import get_available_validators

        validators = get_available_validators()

        # Built-in validators
        assert "MinValueValidator" in validators
        assert "MaxValueValidator" in validators

        # Custom validators from settings
        assert "even_number" in validators
        assert "custom_range" in validators
        assert "positive" in validators

        # Check display names
        assert validators["MinValueValidator"] == "Valeur minimale"
        assert "custom" in validators["even_number"].lower()

    def test_import_validator_function(self):
        """Test importing a function validator"""
        from django_app_parameter.utils import import_validator

        validator = import_validator("tests.test_validators.validate_even_number")
        assert callable(validator)

        # Test it works
        validator(4)  # Should not raise

        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            validator(3)  # Should raise

    def test_import_validator_class(self):
        """Test importing a class validator"""
        from django_app_parameter.utils import import_validator

        ValidatorClass = import_validator("tests.test_validators.CustomRangeValidator")
        assert callable(ValidatorClass)

        # Instantiate and test
        validator = ValidatorClass(min_value=0, max_value=10)
        validator(5)  # Should not raise

        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            validator(15)  # Should raise

    def test_invalid_validator_path_raises_import_error(self):
        """Test that invalid validator paths raise ImportError"""
        from django_app_parameter.utils import import_validator

        # Invalid module path
        with pytest.raises(ImportError, match="Cannot import module"):
            import_validator("nonexistent.module.validator")

        # Invalid validator name
        with pytest.raises(AttributeError, match="does not have attribute"):
            import_validator("tests.test_validators.nonexistent_validator")

        # Invalid path format
        with pytest.raises(ImportError, match="Invalid validator path"):
            import_validator("invalid_path")

    def test_validator_caching_mechanism(self, custom_validators_settings):
        """Test that validators are cached after first import"""
        from django_app_parameter.utils import (
            clear_validator_cache,
            get_validator_from_registry,
        )

        # Clear cache first
        clear_validator_cache()

        # First call should import
        validator1 = get_validator_from_registry("even_number")
        assert validator1 is not None

        # Second call should return cached version (same object)
        validator2 = get_validator_from_registry("even_number")
        assert validator1 is validator2

        # Clear cache and verify it's re-imported
        clear_validator_cache()
        validator3 = get_validator_from_registry("even_number")
        assert validator3 is not None

    def test_admin_form_validator_choices_include_custom(
        self, custom_validators_settings
    ):
        """Test that admin form includes custom validators in choices"""
        from django_app_parameter.admin import ParameterValidatorForm

        form = ParameterValidatorForm()

        # Get the validator_type field choices
        choices = form.fields["validator_type"].choices

        # Convert to dict for easier testing
        choice_keys = [key for key, _ in choices]

        # Built-in validators
        assert "MinValueValidator" in choice_keys
        assert "MaxValueValidator" in choice_keys

        # Custom validators
        assert "even_number" in choice_keys
        assert "custom_range" in choice_keys
        assert "positive" in choice_keys

    def test_unknown_validator_type_raises_error(self):
        """Test that unknown validator_type raises ValueError"""
        param = Parameter.objects.create(
            name="test_unknown",
            value="10",
            value_type=Parameter.TYPES.INT,
        )
        validator = ParameterValidator.objects.create(
            parameter=param,
            validator_type="unknown_validator",  # Does not exist
        )

        with pytest.raises(ValueError, match="Unknown validator type"):
            validator.get_validator()

    def test_custom_validator_with_no_params(self, custom_validators_settings):
        """Test custom function validator that takes no params"""
        param = Parameter.objects.create(
            name="test_positive",
            value="5",
            value_type=Parameter.TYPES.INT,
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="positive",  # Function validator, no params
        )

        # Should work with positive numbers
        param.set(10)
        assert param.int() == 10

        # Should fail with zero or negative
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            param.set(0)

        with pytest.raises(ValidationError):
            param.set(-5)


class TestParameterManagerDumpLoad:
    """Test the load_from_json and dump_to_json methods of ParameterManager"""

    @pytest.mark.django_db
    def test_dump_to_json_basic(self):
        """Test basic dump_to_json functionality"""
        # Create test parameters
        Parameter.objects.create(
            name="Test Param 1",
            slug="TEST_PARAM_1",
            value="value1",
            value_type="STR",
            description="Test description",
            is_global=True,
        )
        Parameter.objects.create(
            name="Test Param 2",
            slug="TEST_PARAM_2",
            value="42",
            value_type="INT",
            description="",
            is_global=False,
        )

        # Dump to JSON
        result = Parameter.objects.dump_to_json()

        # Verify result structure
        assert isinstance(result, list)
        assert len(result) == 2

        # Verify first parameter
        param1 = result[0]
        assert param1["name"] == "Test Param 1"
        assert param1["slug"] == "TEST_PARAM_1"
        assert param1["value"] == "value1"
        assert param1["value_type"] == "STR"
        assert param1["description"] == "Test description"
        assert param1["is_global"] is True

        # Verify second parameter
        param2 = result[1]
        assert param2["name"] == "Test Param 2"
        assert param2["slug"] == "TEST_PARAM_2"
        assert param2["value"] == "42"
        assert param2["value_type"] == "INT"

    @pytest.mark.django_db
    def test_dump_to_json_with_validators(self):
        """Test dump_to_json includes validators"""
        param = Parameter.objects.create(
            name="Test Param",
            slug="TEST_PARAM",
            value="10",
            value_type="INT",
        )

        # Add validators
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="MinValueValidator",
            validator_params={"limit_value": 5},
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="MaxValueValidator",
            validator_params={"limit_value": 100},
        )

        # Dump to JSON
        result = Parameter.objects.dump_to_json()

        assert len(result) == 1
        param_data = result[0]

        # Verify validators are included
        assert "validators" in param_data
        assert len(param_data["validators"]) == 2

        validators = param_data["validators"]
        assert validators[0]["validator_type"] == "MinValueValidator"
        assert validators[0]["validator_params"] == {"limit_value": 5}
        assert validators[1]["validator_type"] == "MaxValueValidator"
        assert validators[1]["validator_params"] == {"limit_value": 100}

    @pytest.mark.django_db
    def test_dump_to_json_without_validators(self):
        """Test dump_to_json excludes validators key when no validators"""
        Parameter.objects.create(
            name="Test Param",
            slug="TEST_PARAM",
            value="test",
        )

        result = Parameter.objects.dump_to_json()

        assert len(result) == 1
        # No validators key should be present
        assert "validators" not in result[0]

    @pytest.mark.django_db
    def test_dump_to_json_empty_database(self):
        """Test dump_to_json with empty database"""
        result = Parameter.objects.dump_to_json()

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.django_db
    def test_load_from_json_basic(self):
        """Test basic load_from_json functionality"""
        data = [
            {
                "name": "New Param",
                "value": "test value",
                "value_type": "STR",
                "description": "Test description",
                "is_global": True,
            }
        ]

        Parameter.objects.load_from_json(data)

        # Verify parameter was created
        param = Parameter.objects.get(slug="NEW_PARAM")
        assert param.name == "New Param"
        assert param.value == "test value"
        assert param.value_type == "STR"
        assert param.description == "Test description"
        assert param.is_global is True

    @pytest.mark.django_db
    def test_load_from_json_with_custom_slug(self):
        """Test load_from_json with custom slug"""
        data = [
            {
                "name": "Custom Slug Param",
                "slug": "CUSTOM_SLUG",
                "value": "test",
            }
        ]

        Parameter.objects.load_from_json(data)

        param = Parameter.objects.get(slug="CUSTOM_SLUG")
        assert param.name == "Custom Slug Param"
        assert param.slug == "CUSTOM_SLUG"

    @pytest.mark.django_db
    def test_load_from_json_update_existing(self):
        """Test load_from_json updates existing parameters by default"""
        # Create initial parameter
        Parameter.objects.create(
            name="Test Param",
            slug="TEST_PARAM",
            value="old value",
        )

        # Load with updated value
        data = [
            {
                "slug": "TEST_PARAM",
                "name": "Updated Name",
                "value": "new value",
            }
        ]

        Parameter.objects.load_from_json(data, do_update=True)

        # Verify parameter was updated
        param = Parameter.objects.get(slug="TEST_PARAM")
        assert param.name == "Updated Name"
        assert param.value == "new value"

    @pytest.mark.django_db
    def test_load_from_json_no_update(self):
        """Test load_from_json with do_update=False"""
        # Create initial parameter
        Parameter.objects.create(
            name="Test Param",
            slug="TEST_PARAM",
            value="old value",
        )

        # Try to load with updated value but no_update
        data = [
            {
                "slug": "TEST_PARAM",
                "name": "Updated Name",
                "value": "new value",
            }
        ]

        Parameter.objects.load_from_json(data, do_update=False)

        # Verify parameter was NOT updated
        param = Parameter.objects.get(slug="TEST_PARAM")
        assert param.name == "Test Param"  # Original name
        assert param.value == "old value"  # Original value

    @pytest.mark.django_db
    def test_load_from_json_with_validators(self):
        """Test load_from_json creates validators"""
        data = [
            {
                "name": "Validated Param",
                "value": "10",
                "value_type": "INT",
                "validators": [
                    {
                        "validator_type": "MinValueValidator",
                        "validator_params": {"limit_value": 5},
                    },
                    {
                        "validator_type": "MaxValueValidator",
                        "validator_params": {"limit_value": 100},
                    },
                ],
            }
        ]

        Parameter.objects.load_from_json(data)

        param = Parameter.objects.get(slug="VALIDATED_PARAM")
        validators = param.validators.all()

        assert validators.count() == 2
        assert validators[0].validator_type == "MinValueValidator"
        assert validators[0].validator_params == {"limit_value": 5}
        assert validators[1].validator_type == "MaxValueValidator"
        assert validators[1].validator_params == {"limit_value": 100}

    @pytest.mark.django_db
    def test_load_from_json_replaces_validators(self):
        """Test load_from_json replaces existing validators"""
        # Create parameter with validators
        param = Parameter.objects.create(
            name="Test Param",
            slug="TEST_PARAM",
            value="10",
            value_type="INT",
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="MinValueValidator",
            validator_params={"limit_value": 1},
        )

        # Load with different validators
        data = [
            {
                "slug": "TEST_PARAM",
                "name": "Test Param",
                "value": "10",
                "value_type": "INT",
                "validators": [
                    {
                        "validator_type": "MaxValueValidator",
                        "validator_params": {"limit_value": 100},
                    }
                ],
            }
        ]

        Parameter.objects.load_from_json(data)

        # Verify old validators are gone and new ones are present
        param = Parameter.objects.get(slug="TEST_PARAM")
        validators = param.validators.all()

        assert validators.count() == 1
        assert validators[0].validator_type == "MaxValueValidator"

    @pytest.mark.django_db
    def test_load_from_json_removes_validators_when_not_in_json(self):
        """Test load_from_json removes validators when not in JSON"""
        # Create parameter with validators
        param = Parameter.objects.create(
            name="Test Param",
            slug="TEST_PARAM",
            value="10",
            value_type="INT",
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="MinValueValidator",
            validator_params={"limit_value": 1},
        )

        # Load without validators key
        data = [
            {
                "slug": "TEST_PARAM",
                "name": "Test Param",
                "value": "10",
                "value_type": "INT",
            }
        ]

        Parameter.objects.load_from_json(data)

        # Verify validators are removed
        param = Parameter.objects.get(slug="TEST_PARAM")
        assert param.validators.count() == 0

    @pytest.mark.django_db
    def test_dump_load_roundtrip(self):
        """Test that dump → load → dump produces identical results"""
        # Create test parameters with validators
        param1 = Parameter.objects.create(
            name="Param 1",
            slug="PARAM_1",
            value="test",
            value_type="STR",
            description="Description 1",
            is_global=True,
        )
        ParameterValidator.objects.create(
            parameter=param1,
            validator_type="MinLengthValidator",
            validator_params={"limit_value": 3},
        )

        Parameter.objects.create(
            name="Param 2",
            slug="PARAM_2",
            value="42",
            value_type="INT",
            description="Description 2",
            is_global=False,
        )

        # First dump
        dump1 = Parameter.objects.dump_to_json()

        # Clear database and reload
        Parameter.objects.all().delete()
        Parameter.objects.load_from_json(dump1)

        # Second dump
        dump2 = Parameter.objects.dump_to_json()

        # Compare dumps (should be identical)
        assert dump1 == dump2

    @pytest.mark.django_db
    def test_load_from_json_multiple_parameters(self):
        """Test load_from_json with multiple parameters"""
        data = [
            {"name": "Param 1", "value": "value1"},
            {"name": "Param 2", "value": "value2"},
            {"name": "Param 3", "value": "value3"},
        ]

        Parameter.objects.load_from_json(data)

        assert Parameter.objects.count() == 3
        assert Parameter.objects.filter(slug="PARAM_1").exists()
        assert Parameter.objects.filter(slug="PARAM_2").exists()
        assert Parameter.objects.filter(slug="PARAM_3").exists()
