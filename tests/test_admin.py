"""Tests for admin forms and helpers"""

from decimal import Decimal

import pytest
from django import forms

from django_app_parameter.admin import (
    ParameterAdmin,
    ParameterCreateForm,
    ParameterEditForm,
    ParameterValidatorForm,
)
from django_app_parameter.models import Parameter, ParameterValidator


@pytest.mark.django_db
class TestParameterCreateForm:
    """Tests for ParameterCreateForm"""

    def test_create_form_fields(self):
        """Test that create form has correct fields"""
        form = ParameterCreateForm()
        assert "name" in form.fields
        assert "slug" in form.fields
        assert "value_type" in form.fields
        assert "description" in form.fields
        assert "is_global" in form.fields
        # Should not have 'value' field
        assert "value" not in form.fields

    def test_create_form_slug_optional(self):
        """Test that slug is optional in create form"""
        form = ParameterCreateForm()
        assert form.fields["slug"].required is False

    def test_create_form_valid_data(self):
        """Test create form with valid data"""
        form = ParameterCreateForm(
            data={
                "name": "Test Param",
                "value_type": "STR",
                "description": "Test description",
                "is_global": True,
            }
        )
        assert form.is_valid()

    def test_create_form_with_custom_slug(self):
        """Test create form with custom slug"""
        form = ParameterCreateForm(
            data={
                "name": "Test Param",
                "slug": "CUSTOM_SLUG",
                "value_type": "INT",
            }
        )
        assert form.is_valid()


@pytest.mark.django_db
class TestParameterEditForm:
    """Tests for ParameterEditForm and its helper methods"""

    def test_edit_form_fields(self):
        """Test that edit form has correct fields"""
        param = Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="10",
            value_type="INT",
        )
        form = ParameterEditForm(instance=param)
        assert "name" in form.fields
        assert "description" in form.fields
        assert "value" in form.fields
        assert "is_global" in form.fields
        # Should not have slug or value_type (readonly in admin)
        assert "slug" not in form.fields
        assert "value_type" not in form.fields

    def test_convert_value_to_type_bool(self):
        """Test _convert_value_to_type with boolean"""
        param = Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="1",
            value_type="BOO",
        )
        form = ParameterEditForm(instance=param)

        # Test with actual bool
        result = form._convert_value_to_type(True, "BOO")
        assert result is True

        # Test with string
        result = form._convert_value_to_type("1", "BOO")
        assert isinstance(result, bool)

    def test_convert_value_to_type_int(self):
        """Test _convert_value_to_type with int"""
        param = Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="42",
            value_type="INT",
        )
        form = ParameterEditForm(instance=param)

        result = form._convert_value_to_type("42", "INT")
        assert result == 42
        assert isinstance(result, int)

    def test_convert_value_to_type_float(self):
        """Test _convert_value_to_type with float"""
        param = Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="3.14",
            value_type="FLT",
        )
        form = ParameterEditForm(instance=param)

        result = form._convert_value_to_type("3.14", "FLT")
        assert result == 3.14
        assert isinstance(result, float)

    def test_convert_value_to_type_decimal(self):
        """Test _convert_value_to_type with decimal"""
        param = Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="99.99",
            value_type="DCL",
        )
        form = ParameterEditForm(instance=param)

        result = form._convert_value_to_type("99.99", "DCL")
        assert result == Decimal("99.99")
        assert isinstance(result, Decimal)

    def test_convert_value_to_type_percentage(self):
        """Test _convert_value_to_type with percentage"""
        param = Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="75.5",
            value_type="PCT",
        )
        form = ParameterEditForm(instance=param)

        result = form._convert_value_to_type("75.5", "PCT")
        assert result == 75.5
        assert isinstance(result, float)

    def test_convert_value_to_type_string(self):
        """Test _convert_value_to_type with string types"""
        param = Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="test",
            value_type="STR",
        )
        form = ParameterEditForm(instance=param)

        result = form._convert_value_to_type("test value", "STR")
        assert result == "test value"
        assert isinstance(result, str)

    def test_clean_value_with_validators(self):
        """Test clean_value runs validators"""
        param = Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="50",
            value_type="INT",
        )
        ParameterValidator.objects.create(
            parameter=param,
            validator_type="MinValueValidator",
            validator_params={"limit_value": 10},
        )

        # Valid value
        form = ParameterEditForm(data={"name": "Test", "value": "100"}, instance=param)
        assert form.is_valid()

        # Invalid value
        form = ParameterEditForm(data={"name": "Test", "value": "5"}, instance=param)
        assert not form.is_valid()
        assert "value" in form.errors

    def test_clean_value_with_multiple_validators(self):
        """Test clean_value with multiple validators"""
        param = Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="50",
            value_type="INT",
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

        # Valid value
        form = ParameterEditForm(data={"name": "Test", "value": "50"}, instance=param)
        assert form.is_valid()

        # Too low
        form = ParameterEditForm(data={"name": "Test", "value": "5"}, instance=param)
        assert not form.is_valid()

        # Too high
        form = ParameterEditForm(data={"name": "Test", "value": "150"}, instance=param)
        assert not form.is_valid()

    def test_clean_value_type_conversion_error(self):
        """Test clean_value handles type conversion errors"""
        param = Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="42",
            value_type="INT",
        )

        # Try to set non-integer value
        form = ParameterEditForm(
            data={"name": "Test", "value": "not_a_number"}, instance=param
        )
        assert not form.is_valid()
        assert "value" in form.errors


@pytest.mark.django_db
class TestParameterValidatorForm:
    """Tests for ParameterValidatorForm"""

    def test_validator_form_has_dynamic_choices(self):
        """Test that validator form has dynamic choices"""
        form = ParameterValidatorForm()

        # Should have validator_type field with choices
        assert "validator_type" in form.fields
        assert isinstance(form.fields["validator_type"], forms.ChoiceField)

        choices = form.fields["validator_type"].choices
        choice_values = [choice[0] for choice in choices]

        # Should include built-in validators
        assert "MinValueValidator" in choice_values
        assert "MaxValueValidator" in choice_values
        assert "EmailValidator" in choice_values

    def test_validator_form_clean_validator_type_valid(self):
        """Test clean_validator_type with valid validator"""
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="10", value_type="INT"
        )

        form = ParameterValidatorForm(
            data={
                "validator_type": "MinValueValidator",
                "validator_params": {"limit_value": 5},
            }
        )
        # Set parameter manually since we're not using ModelForm.save()
        form.instance.parameter = param

        assert form.is_valid()

    def test_validator_form_clean_validator_type_empty(self):
        """Test clean_validator_type with empty value"""
        form = ParameterValidatorForm(
            data={
                "validator_type": "",
                "validator_params": {},
            }
        )

        assert not form.is_valid()
        assert "validator_type" in form.errors

    def test_validator_form_with_custom_validators(self, settings):
        """Test that custom validators appear in choices"""
        settings.DJANGO_APP_PARAMETER = {
            "validators": {"even_number": "tests.test_validators.validate_even_number"}
        }

        form = ParameterValidatorForm()
        choices = form.fields["validator_type"].choices
        choice_values = [choice[0] for choice in choices]

        # Should include custom validator
        assert "even_number" in choice_values

    def test_validator_form_clean_validator_type_empty_bypassing_choice_field(self):
        """Test clean_validator_type directly with empty value"""
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="10", value_type="INT"
        )

        form = ParameterValidatorForm(
            data={
                "validator_type": "MinValueValidator",
                "validator_params": {"limit_value": 5},
            }
        )
        # Manually set cleaned_data to bypass ChoiceField validation
        form.is_valid()
        form.cleaned_data["validator_type"] = ""

        # Now test clean_validator_type directly
        with pytest.raises(forms.ValidationError, match="sélectionner un validateur"):
            form.clean_validator_type()

    def test_validator_form_clean_validator_type_not_in_available(self, settings):
        """Test clean_validator_type with validator not in available list"""
        settings.DJANGO_APP_PARAMETER = {"validators": {}}

        param = Parameter.objects.create(
            name="Test", slug="TEST", value="10", value_type="INT"
        )

        form = ParameterValidatorForm(
            data={
                "validator_type": "MinValueValidator",
                "validator_params": {"limit_value": 5},
            }
        )
        # Manually set cleaned_data with a non-existent validator
        form.is_valid()
        form.cleaned_data["validator_type"] = "CompletelyCustomValidator"

        # Now test clean_validator_type directly
        with pytest.raises(forms.ValidationError, match="non trouvé"):
            form.clean_validator_type()


@pytest.mark.django_db
class TestParameterAdminHelpers:
    """Tests for ParameterAdmin helper methods"""

    def test_get_field_mapping(self):
        """Test _get_field_mapping returns correct mapping"""
        admin = ParameterAdmin(Parameter, None)
        mapping = admin._get_field_mapping()

        assert mapping["BOO"] == forms.BooleanField
        assert mapping["INT"] == forms.IntegerField
        assert mapping["FLT"] == forms.FloatField
        assert mapping["DCL"] == forms.DecimalField
        assert mapping["DAT"] == forms.DateField
        assert mapping["DTM"] == forms.DateTimeField
        assert mapping["TIM"] == forms.TimeField
        assert mapping["URL"] == forms.URLField
        assert mapping["EML"] == forms.EmailField
        assert mapping["STR"] == forms.CharField

    def test_get_current_value_int(self):
        """Test _get_current_value with INT type"""
        admin = ParameterAdmin(Parameter, None)
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="42", value_type="INT"
        )

        current_value = admin._get_current_value(param)
        assert current_value == 42
        assert isinstance(current_value, int)

    def test_get_current_value_bool(self):
        """Test _get_current_value with BOO type"""
        admin = ParameterAdmin(Parameter, None)
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="1", value_type="BOO"
        )

        current_value = admin._get_current_value(param)
        assert current_value is True
        assert isinstance(current_value, bool)

    def test_get_current_value_str(self):
        """Test _get_current_value with STR type"""
        admin = ParameterAdmin(Parameter, None)
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="test string", value_type="STR"
        )

        current_value = admin._get_current_value(param)
        assert current_value == "test string"
        assert isinstance(current_value, str)

    def test_get_current_value_invalid_falls_back(self):
        """Test _get_current_value falls back to raw value on error"""
        admin = ParameterAdmin(Parameter, None)
        # Create param with invalid INT value
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="invalid", value_type="INT"
        )

        current_value = admin._get_current_value(param)
        # Should fall back to raw value
        assert current_value == "invalid"

    def test_get_field_for_value_type_json(self):
        """Test _get_field_for_value_type with JSON type"""
        admin = ParameterAdmin(Parameter, None)
        param = Parameter.objects.create(
            name="Test", slug="TEST", value='{"key": "value"}', value_type="JSN"
        )

        field_mapping = admin._get_field_mapping()
        field_class, field_kwargs = admin._get_field_for_value_type(
            param, field_mapping
        )

        assert field_class == forms.CharField
        assert isinstance(field_kwargs["widget"], forms.Textarea)
        assert field_kwargs["widget"].attrs["rows"] == 4

    def test_get_field_for_value_type_dict(self):
        """Test _get_field_for_value_type with DICT type"""
        admin = ParameterAdmin(Parameter, None)
        param = Parameter.objects.create(
            name="Test", slug="TEST", value='{"key": "value"}', value_type="DCT"
        )

        field_mapping = admin._get_field_mapping()
        field_class, field_kwargs = admin._get_field_for_value_type(
            param, field_mapping
        )

        assert field_class == forms.CharField
        assert isinstance(field_kwargs["widget"], forms.Textarea)

    def test_get_field_for_value_type_list(self):
        """Test _get_field_for_value_type with LIST type"""
        admin = ParameterAdmin(Parameter, None)
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="a, b, c", value_type="LST"
        )

        field_mapping = admin._get_field_mapping()
        field_class, field_kwargs = admin._get_field_for_value_type(
            param, field_mapping
        )

        assert field_class == forms.CharField
        assert "virgules" in field_kwargs["help_text"]

    def test_get_field_for_value_type_percentage(self):
        """Test _get_field_for_value_type with PERCENTAGE type"""
        admin = ParameterAdmin(Parameter, None)
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="75.5", value_type="PCT"
        )

        field_mapping = admin._get_field_mapping()
        field_class, field_kwargs = admin._get_field_for_value_type(
            param, field_mapping
        )

        assert field_class == forms.FloatField
        assert field_kwargs["min_value"] == 0
        assert field_kwargs["max_value"] == 100
        assert "0 et 100" in field_kwargs["help_text"]

    def test_get_field_for_value_type_duration(self):
        """Test _get_field_for_value_type with DURATION type"""
        admin = ParameterAdmin(Parameter, None)
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="3600", value_type="DUR"
        )

        field_mapping = admin._get_field_mapping()
        field_class, field_kwargs = admin._get_field_for_value_type(
            param, field_mapping
        )

        assert field_class == forms.FloatField
        assert "secondes" in field_kwargs["help_text"]

    def test_get_readonly_fields_creating(self):
        """Test get_readonly_fields when creating new parameter"""
        admin = ParameterAdmin(Parameter, None)
        from django.http import HttpRequest

        request = HttpRequest()

        readonly = admin.get_readonly_fields(request, obj=None)
        # When creating, no fields should be readonly
        assert readonly == ()

    def test_get_readonly_fields_editing(self):
        """Test get_readonly_fields when editing existing parameter"""
        admin = ParameterAdmin(Parameter, None)
        from django.http import HttpRequest

        request = HttpRequest()
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="test", value_type="STR"
        )

        readonly = admin.get_readonly_fields(request, obj=param)
        # When editing, slug and value_type should be readonly
        assert "slug" in readonly
        assert "value_type" in readonly

    def test_get_inlines_creating(self):
        """Test get_inlines when creating new parameter"""
        admin = ParameterAdmin(Parameter, None)
        from django.http import HttpRequest

        request = HttpRequest()

        inlines = admin.get_inlines(request, obj=None)
        # When creating, no inlines
        assert inlines == []

    def test_get_inlines_editing(self):
        """Test get_inlines when editing existing parameter"""
        admin = ParameterAdmin(Parameter, None)
        from django.http import HttpRequest

        request = HttpRequest()
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="test", value_type="STR"
        )

        inlines = admin.get_inlines(request, obj=param)
        # When editing, should have validator inline
        assert len(inlines) == 1

    def test_get_current_value_date(self):
        """Test _get_current_value with DATE type"""
        from datetime import date

        admin = ParameterAdmin(Parameter, None)
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="2024-01-15", value_type="DAT"
        )

        current_value = admin._get_current_value(param)
        assert current_value == date(2024, 1, 15)
        assert isinstance(current_value, date)

    def test_get_current_value_datetime(self):
        """Test _get_current_value with DATETIME type"""
        from datetime import datetime

        admin = ParameterAdmin(Parameter, None)
        param = Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="2024-01-15T10:30:00",
            value_type="DTM",
        )

        current_value = admin._get_current_value(param)
        assert current_value == datetime(2024, 1, 15, 10, 30, 0)
        assert isinstance(current_value, datetime)

    def test_get_current_value_time(self):
        """Test _get_current_value with TIME type"""
        from datetime import time

        admin = ParameterAdmin(Parameter, None)
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="14:30:00", value_type="TIM"
        )

        current_value = admin._get_current_value(param)
        assert current_value == time(14, 30, 0)
        assert isinstance(current_value, time)

    def test_get_current_value_float(self):
        """Test _get_current_value with FLOAT type"""
        admin = ParameterAdmin(Parameter, None)
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="3.14", value_type="FLT"
        )

        current_value = admin._get_current_value(param)
        assert current_value == 3.14
        assert isinstance(current_value, float)

    def test_get_current_value_decimal(self):
        """Test _get_current_value with DECIMAL type"""
        admin = ParameterAdmin(Parameter, None)
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="99.99", value_type="DCL"
        )

        current_value = admin._get_current_value(param)
        assert current_value == Decimal("99.99")
        assert isinstance(current_value, Decimal)

    def test_get_current_value_duration(self):
        """Test _get_current_value with DURATION type"""
        admin = ParameterAdmin(Parameter, None)
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="3600", value_type="DUR"
        )

        current_value = admin._get_current_value(param)
        # Returns total_seconds()
        assert current_value == 3600.0
        assert isinstance(current_value, float)

    def test_get_current_value_percentage(self):
        """Test _get_current_value with PERCENTAGE type"""
        admin = ParameterAdmin(Parameter, None)
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="75.5", value_type="PCT"
        )

        current_value = admin._get_current_value(param)
        assert current_value == 75.5
        assert isinstance(current_value, float)

    def test_validator_form_clean_validator_type_invalid(self):
        """Test clean_validator_type with invalid validator"""
        form = ParameterValidatorForm(
            data={
                "validator_type": "NonExistentValidator",
                "validator_params": {},
            }
        )

        assert not form.is_valid()
        assert "validator_type" in form.errors
        # Django's ChoiceField validation message
        assert "not one of the available choices" in str(form.errors["validator_type"])

    def test_clean_value_no_instance(self):
        """Test clean_value when instance is None"""
        form = ParameterEditForm(data={"name": "Test", "value": "test"})
        # Form needs to be validated first to populate cleaned_data
        form.is_valid()
        # Should return value as-is when no instance
        cleaned_value = form.clean_value()
        assert cleaned_value == "test"


@pytest.mark.django_db
class TestParameterAdminGetForm:
    """Tests for ParameterAdmin.get_form method"""

    def test_get_form_creating(self):
        """Test get_form when creating new parameter"""
        from django.contrib.admin.sites import AdminSite
        from django.http import HttpRequest

        admin = ParameterAdmin(Parameter, AdminSite())
        request = HttpRequest()

        form_class = admin.get_form(request, obj=None)

        # Should use ParameterCreateForm
        assert form_class._meta.model == Parameter
        assert "name" in form_class.base_fields
        assert "slug" in form_class.base_fields
        assert "value_type" in form_class.base_fields

    def test_get_form_editing_with_else_branch(self):
        """Test get_form editing with value_type that hits else branch"""
        from django.contrib.admin.sites import AdminSite
        from django.http import HttpRequest

        admin = ParameterAdmin(Parameter, AdminSite())
        request = HttpRequest()

        # Create a parameter with EMAIL type (should hit else branch in _get_field_for_value_type)
        param = Parameter.objects.create(
            name="Test Email",
            slug="TEST_EMAIL",
            value="test@example.com",
            value_type="EML",
        )

        form_class = admin.get_form(request, obj=param, change=True)

        # Should have customized value field
        assert "value" in form_class.base_fields
        # EMAIL should use EmailField from mapping
        assert isinstance(form_class.base_fields["value"], forms.EmailField)


@pytest.mark.django_db
class TestParameterAdminSaveModel:
    """Tests for ParameterAdmin.save_model method"""

    def test_save_model_update_existing(self):
        """Test save_model when updating existing parameter"""
        from django.contrib.admin.sites import AdminSite
        from django.http import HttpRequest

        admin = ParameterAdmin(Parameter, AdminSite())
        request = HttpRequest()

        # Use STR type to avoid conversion issues in this test
        param = Parameter.objects.create(
            name="Test", slug="TEST", value="old_value", value_type="STR"
        )

        # Create form with new value
        form = ParameterEditForm(
            data={"name": "Test", "value": "new_value", "description": "", "is_global": False},
            instance=param,
        )
        assert form.is_valid()

        # Save using admin's save_model
        admin.save_model(request, param, form, change=True)

        # Value should be updated
        param.refresh_from_db()
        assert param.value == "new_value"

    def test_save_model_create_new_with_defaults(self):
        """Test save_model when creating new parameter with default values"""
        from django.contrib.admin.sites import AdminSite
        from django.http import HttpRequest

        admin = ParameterAdmin(Parameter, AdminSite())
        request = HttpRequest()

        # Create a new parameter without value
        param = Parameter(name="New Param", slug="NEW_PARAM", value_type="INT", value="")

        form = ParameterCreateForm(
            data={
                "name": "New Param",
                "slug": "NEW_PARAM",
                "value_type": "INT",
                "description": "",
                "is_global": False,
            },
            instance=param,
        )
        assert form.is_valid()

        # Save using admin's save_model
        admin.save_model(request, param, form, change=False)

        # Should have default value
        param.refresh_from_db()
        assert param.value == "0"  # Default for INT

    def test_save_model_create_bool_type(self):
        """Test save_model creates parameter with BOO type default"""
        from django.contrib.admin.sites import AdminSite
        from django.http import HttpRequest

        admin = ParameterAdmin(Parameter, AdminSite())
        request = HttpRequest()

        param = Parameter(
            name="Bool Param", slug="BOOL_PARAM", value_type="BOO", value=""
        )

        form = ParameterCreateForm(
            data={
                "name": "Bool Param",
                "slug": "BOOL_PARAM",
                "value_type": "BOO",
                "description": "",
                "is_global": False,
            },
            instance=param,
        )
        assert form.is_valid()

        admin.save_model(request, param, form, change=False)

        param.refresh_from_db()
        assert param.value == "0"  # Default for BOO
