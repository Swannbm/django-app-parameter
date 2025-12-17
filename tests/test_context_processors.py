"""Tests for context processors"""

import pytest
from django.http import HttpRequest
from django.test import RequestFactory

from django_app_parameter.context_processors import add_global_parameter_context
from django_app_parameter.models import Parameter


@pytest.fixture
def request_factory() -> RequestFactory:
    """Fixture providing a Django RequestFactory instance"""
    return RequestFactory()


@pytest.fixture
def dummy_request(request_factory: RequestFactory) -> HttpRequest:
    """Fixture providing a dummy HTTP request"""
    return request_factory.get("/")


@pytest.mark.django_db
class TestContextProcessors:
    """Test suite for context processors"""

    def test_empty_context_when_no_global_parameters(
        self, dummy_request: HttpRequest
    ) -> None:
        """Test that context is empty when no global parameters exist"""
        context = add_global_parameter_context(dummy_request)
        assert context == {}

    def test_non_global_parameters_not_included(
        self, dummy_request: HttpRequest
    ) -> None:
        """Test that non-global parameters are not included in context"""
        Parameter.objects.create(
            name="non-global param",
            slug="NON_GLOBAL",
            value="test",
            is_global=False,
        )
        context = add_global_parameter_context(dummy_request)
        assert "NON_GLOBAL" not in context
        assert context == {}

    def test_string_parameter_type(self, dummy_request: HttpRequest) -> None:
        """Test that string parameters are correctly typed"""
        Parameter.objects.create(
            name="string param",
            slug="STRING_PARAM",
            value="hello world",
            value_type=Parameter.TYPES.STR,
            is_global=True,
        )
        context = add_global_parameter_context(dummy_request)

        assert "STRING_PARAM" in context
        assert context["STRING_PARAM"] == "hello world"
        assert isinstance(context["STRING_PARAM"], str)

    def test_int_parameter_type(self, dummy_request: HttpRequest) -> None:
        """Test that integer parameters are correctly typed"""
        Parameter.objects.create(
            name="int param",
            slug="INT_PARAM",
            value="42",
            value_type=Parameter.TYPES.INT,
            is_global=True,
        )
        context = add_global_parameter_context(dummy_request)

        assert "INT_PARAM" in context
        assert context["INT_PARAM"] == 42
        assert isinstance(context["INT_PARAM"], int)

    def test_bool_parameter_type_true(self, dummy_request: HttpRequest) -> None:
        """Test that boolean True parameters are correctly typed"""
        Parameter.objects.create(
            name="bool param",
            slug="BOOL_PARAM",
            value="True",
            value_type=Parameter.TYPES.BOO,
            is_global=True,
        )
        context = add_global_parameter_context(dummy_request)

        assert "BOOL_PARAM" in context
        assert context["BOOL_PARAM"] is True
        assert isinstance(context["BOOL_PARAM"], bool)

    def test_bool_parameter_type_false(self, dummy_request: HttpRequest) -> None:
        """Test that boolean False parameters are correctly typed"""
        Parameter.objects.create(
            name="bool param",
            slug="BOOL_PARAM_FALSE",
            value="False",
            value_type=Parameter.TYPES.BOO,
            is_global=True,
        )
        context = add_global_parameter_context(dummy_request)

        assert "BOOL_PARAM_FALSE" in context
        assert context["BOOL_PARAM_FALSE"] is False
        assert isinstance(context["BOOL_PARAM_FALSE"], bool)

    def test_mixed_global_and_non_global_parameters(
        self, dummy_request: HttpRequest
    ) -> None:
        """Test that only global parameters are included when mixed with non-global"""
        Parameter.objects.bulk_create(
            [
                Parameter(
                    name="global param",
                    slug="GLOBAL_PARAM",
                    value="global",
                    is_global=True,
                ),
                Parameter(
                    name="non global param",
                    slug="NON_GLOBAL_PARAM",
                    value="non-global",
                    is_global=False,
                ),
                Parameter(
                    name="another global",
                    slug="ANOTHER_GLOBAL",
                    value="123",
                    value_type=Parameter.TYPES.INT,
                    is_global=True,
                ),
            ]
        )
        context = add_global_parameter_context(dummy_request)

        assert len(context) == 2
        assert "GLOBAL_PARAM" in context
        assert context["GLOBAL_PARAM"] == "global"
        assert "ANOTHER_GLOBAL" in context
        assert context["ANOTHER_GLOBAL"] == 123
        assert "NON_GLOBAL_PARAM" not in context
