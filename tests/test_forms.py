"""Tests for forms module: FieldConfig, create_parameter_field, and registry."""

import pytest
from django import forms

from django_app_parameter.forms import (
    DEFAULT_FIELD_CONFIG,
    FIELD_TYPE_REGISTRY,
    FieldConfig,
    create_parameter_field,
    get_field_config_for_type,
)
from django_app_parameter.models import TYPES, Parameter


class TestFieldConfig:
    """Tests for FieldConfig dataclass."""

    def test_default_values(self):
        """Test FieldConfig default values."""
        config = FieldConfig()
        assert config.field_class == forms.CharField
        assert config.widget is None
        assert config.extra_kwargs == {}
        assert config.help_text == ""

    def test_custom_values(self):
        """Test FieldConfig with custom values."""
        widget = forms.Textarea()
        config = FieldConfig(
            field_class=forms.IntegerField,
            widget=widget,
            extra_kwargs={"min_value": 0},
            help_text="Test help",
        )
        assert config.field_class == forms.IntegerField
        assert config.widget == widget
        assert config.extra_kwargs == {"min_value": 0}
        assert config.help_text == "Test help"

    def test_is_frozen(self):
        """Test that FieldConfig is immutable."""
        config = FieldConfig()
        with pytest.raises(AttributeError):
            config.field_class = forms.IntegerField  # type: ignore[misc]


class TestFieldTypeRegistry:
    """Tests for FIELD_TYPE_REGISTRY."""

    def test_all_types_have_config(self):
        """Test that all TYPES have a configuration in the registry."""
        for type_code in [
            TYPES.STR,
            TYPES.INT,
            TYPES.FLT,
            TYPES.DCL,
            TYPES.BOO,
            TYPES.DATE,
            TYPES.DATETIME,
            TYPES.TIME,
            TYPES.URL,
            TYPES.EMAIL,
            TYPES.PATH,
            TYPES.JSN,
            TYPES.DICT,
            TYPES.LIST,
            TYPES.DURATION,
            TYPES.PERCENTAGE,
        ]:
            assert type_code in FIELD_TYPE_REGISTRY

    def test_int_config(self):
        """Test INT type configuration."""
        config = FIELD_TYPE_REGISTRY[TYPES.INT]
        assert config.field_class == forms.IntegerField

    def test_percentage_config(self):
        """Test PERCENTAGE type has min/max constraints."""
        config = FIELD_TYPE_REGISTRY[TYPES.PERCENTAGE]
        assert config.field_class == forms.FloatField
        assert config.extra_kwargs["min_value"] == 0
        assert config.extra_kwargs["max_value"] == 100

    def test_json_config_has_textarea(self):
        """Test JSN type has Textarea widget."""
        config = FIELD_TYPE_REGISTRY[TYPES.JSN]
        assert config.field_class == forms.CharField
        assert isinstance(config.widget, forms.Textarea)


class TestGetFieldConfigForType:
    """Tests for get_field_config_for_type function."""

    def test_known_type(self):
        """Test get_field_config_for_type with known type."""
        config = get_field_config_for_type(TYPES.INT)
        assert config.field_class == forms.IntegerField

    def test_unknown_type_returns_default(self):
        """Test get_field_config_for_type with unknown type."""
        config = get_field_config_for_type("UNKNOWN_TYPE")
        assert config == DEFAULT_FIELD_CONFIG
        assert config.field_class == forms.CharField


@pytest.mark.django_db
class TestCreateParameterField:
    """Tests for create_parameter_field function."""

    def test_creates_int_field(self):
        """Test create_parameter_field for INT type."""
        param = Parameter.objects.create(
            name="Test Int",
            slug="TEST_INT",
            value="42",
            value_type=TYPES.INT,
        )
        field = create_parameter_field(param)
        assert isinstance(field, forms.IntegerField)
        assert field.initial == 42
        assert field.required is False

    def test_creates_str_field(self):
        """Test create_parameter_field for STR type."""
        param = Parameter.objects.create(
            name="Test Str",
            slug="TEST_STR",
            value="hello",
            value_type=TYPES.STR,
        )
        field = create_parameter_field(param)
        assert isinstance(field, forms.CharField)
        assert field.initial == "hello"

    def test_creates_bool_field(self):
        """Test create_parameter_field for BOO type."""
        param = Parameter.objects.create(
            name="Test Bool",
            slug="TEST_BOOL",
            value="1",
            value_type=TYPES.BOO,
        )
        field = create_parameter_field(param)
        assert isinstance(field, forms.BooleanField)
        assert field.initial is True

    def test_creates_percentage_field_with_constraints(self):
        """Test create_parameter_field for PERCENTAGE type has min/max."""
        param = Parameter.objects.create(
            name="Test Percentage",
            slug="TEST_PERCENTAGE",
            value="50",
            value_type=TYPES.PERCENTAGE,
        )
        field = create_parameter_field(param)
        assert isinstance(field, forms.FloatField)
        assert field.min_value == 0
        assert field.max_value == 100

    def test_creates_json_field_with_textarea(self):
        """Test create_parameter_field for JSN type has Textarea."""
        param = Parameter.objects.create(
            name="Test JSON",
            slug="TEST_JSON",
            value='{"key": "value"}',
            value_type=TYPES.JSN,
        )
        field = create_parameter_field(param)
        assert isinstance(field, forms.CharField)
        assert isinstance(field.widget, forms.Textarea)

    def test_override_required(self):
        """Test create_parameter_field with required=True override."""
        param = Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="test",
            value_type=TYPES.STR,
        )
        field = create_parameter_field(param, required=True)
        assert field.required is True

    def test_override_help_text(self):
        """Test create_parameter_field with custom help_text."""
        param = Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="test",
            value_type=TYPES.STR,
        )
        field = create_parameter_field(param, help_text="Custom help")
        assert field.help_text == "Custom help"

    def test_override_initial(self):
        """Test create_parameter_field with custom initial value."""
        param = Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="original",
            value_type=TYPES.STR,
        )
        field = create_parameter_field(param, initial="overridden")
        assert field.initial == "overridden"
