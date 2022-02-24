from decimal import Decimal
import json
import pytest

from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command

from . import app_parameter
from .models import Parameter
from .context_processors import add_global_parameter_context


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
            value=1,
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
        assert result == float(0.1)
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


@pytest.mark.django_db
class TestParameterManager:
    def test_fixtures(self, params):
        assert Parameter.objects.all().count() == 3

    def test_get_from_slug(self, params):
        params = Parameter.objects.get_from_slug("BIRTH_YEAR")
        assert params.int() == 1983
        with pytest.raises(ImproperlyConfigured):
            Parameter.objects.get_from_slug("NOT_EXISTING")

    def test_create_or_update(self, params):
        existing_param = {
            "name": "year of birth",
            "slug": "BIRTH_YEAR",
            "value": "1984",
        }
        result = Parameter.objects.create_or_update(existing_param, update=False)
        assert result == "Already exists"
        result = Parameter.objects.create_or_update(existing_param)
        assert result == "Already exists, updated"
        new_param = {
            "name": "day of birth",
            "slug": "BIRTH_DAY",
            "value": "27",
            "value_type": Parameter.TYPES.INT,
        }
        result = Parameter.objects.create_or_update(new_param)
        assert result == "Added"

    def test_create_only_name(self):
        result = Parameter.objects.create_or_update({"name": "only_name"})
        assert result == "Added"

    def test_access(self, params):
        assert Parameter.objects.int("BIRTH_YEAR") == 1983
        assert Parameter.objects.str("BIRTH_YEAR") == "1983"
        assert Parameter.objects.float("BIRTH_YEAR") == float("1983")
        assert Parameter.objects.decimal("BIRTH_YEAR") == Decimal("1983")
        assert Parameter.objects.float("BIRTH_YEAR") == float("1983")
        assert Parameter.objects.json("SM_JSON") == [1, 2, 3]


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


@pytest.mark.django_db
class Test_app_parameter:
    def test_read_param(self, params):
        assert isinstance(app_parameter.BIRTH_YEAR, int)
        assert app_parameter.BIRTH_YEAR == 1983
        assert app_parameter.BLOG_TITLE == "my awesome blog"

    def test_set_param(self, params):
        with pytest.raises(Exception):
            app_parameter.BIRTH_YEAR = 1983


@pytest.mark.django_db
class TestContextProcessor:
    def test_context(self, params):
        context = add_global_parameter_context(None)
        assert len(context) == 1
        assert "BIRTH_YEAR" in context
