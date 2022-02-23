from decimal import Decimal
import pytest

from django.core.exceptions import ImproperlyConfigured

from .models import Parameter


class TestParameter:

    @pytest.mark.django_db
    def test_default_slug(self):
        param = Parameter(
            name="testing is good#",
            value="hello world",
        )
        param.save()
        assert param.slug == "TESTING-IS-GOOD"

    def test_default_str(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="hello world",
        )
        assert param.value_type == Parameter.TYPES.STR

    def test_str(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value=1,
        )
        result = param.str()
        assert isinstance(result, str)
        assert result == "1"

    def test_int(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="1",
        )
        result = param.int()
        assert isinstance(result, int)
        assert result == 1

    def test_float(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="0.1",
        )
        result = param.float()
        assert isinstance(result, float)
        assert result == float(0.1)

    def test_decimal(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="0.2",
        )
        result = param.decimal()
        assert isinstance(result, Decimal)
        assert result == Decimal("0.2")

    def json(self):
        param = Parameter(
            name="testing",
            slug="TESTING",
            value="{'hello': ['world', 'testers']}",
        )
        result = param.json()
        assert isinstance(result, dict)
        assert result["hello"][1] == "testers"

    def test_dundo_str(self):
        param = Parameter(
            name="testing",
            value="hello world",
        )
        assert str(param) == "testing"


@pytest.fixture
def params(db):
    params = [
        Parameter(
            name="blog title",
            value="my awesome blog",
        ),
        Parameter(
            name="year of birth",
            slug="BIRTH_YEAR",
            value="1983",
            value_type=Parameter.TYPES.INT,
            is_global=True
        ),
    ]
    Parameter.objects.bulk_create(params)
    return params


@pytest.mark.django_db
class TestAccessingParameter:

    def test_fixtures(self, params):
        assert Parameter.objects.all().count() == 2

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
