"""Tests for Parameter history tracking functionality"""

import pytest
from django_app_parameter.models import Parameter, ParameterHistory


@pytest.mark.django_db
class TestParameterHistory:
    """Tests for ParameterHistory model and enable_history functionality"""

    def test_history_disabled_by_default(self):
        """Test that history is disabled by default"""
        param = Parameter.objects.create(
            name="Test Param",
            value_type=Parameter.TYPES.STR,
            value="initial",
        )
        assert param.enable_history is False

    def test_history_not_saved_when_disabled(self):
        """Test that history is not saved when enable_history=False"""
        param = Parameter.objects.create(
            name="Test Param",
            value_type=Parameter.TYPES.STR,
            value="initial",
            enable_history=False,
        )

        # Modify the value
        param.set_str("updated")

        # Check no history was created
        assert param.history.count() == 0

    def test_history_saved_when_enabled(self):
        """Test that history is saved when enable_history=True"""
        param = Parameter.objects.create(
            name="Test Param",
            value_type=Parameter.TYPES.STR,
            value="initial",
            enable_history=True,
        )

        # Modify the value
        param.set_str("updated")

        # Check history was created
        assert param.history.count() == 1
        history = param.history.first()
        assert history.value == "initial"
        assert history.parameter == param

    def test_history_not_saved_if_value_unchanged(self):
        """Test that history is not saved if value doesn't change"""
        param = Parameter.objects.create(
            name="Test Param",
            value_type=Parameter.TYPES.STR,
            value="same",
            enable_history=True,
        )

        # Set the same value
        param.set_str("same")

        # Check no history was created (value didn't change)
        assert param.history.count() == 0

    def test_history_multiple_changes(self):
        """Test that multiple changes create multiple history entries"""
        param = Parameter.objects.create(
            name="Test Param",
            value_type=Parameter.TYPES.STR,
            value="v1",
            enable_history=True,
        )

        param.set_str("v2")
        param.set_str("v3")
        param.set_str("v4")

        # Check 3 history entries (v1, v2, v3)
        assert param.history.count() == 3
        # Most recent first
        history_values = list(param.history.values_list("value", flat=True))
        assert history_values == ["v3", "v2", "v1"]

    def test_history_with_int_parameter(self):
        """Test history tracking with integer parameter"""
        param = Parameter.objects.create(
            name="Count",
            value_type=Parameter.TYPES.INT,
            value="10",
            enable_history=True,
        )

        param.set_int(20)
        param.set_int(30)

        assert param.history.count() == 2
        history_values = list(param.history.values_list("value", flat=True))
        assert history_values == ["20", "10"]

    def test_history_str_method(self):
        """Test ParameterHistory __str__ method"""
        param = Parameter.objects.create(
            name="Test",
            value_type=Parameter.TYPES.STR,
            value="initial",
            enable_history=True,
        )

        param.set_str("updated")

        history = param.history.first()
        str_repr = str(history)
        # Should contain value and datetime
        assert "initial" in str_repr
        assert "-" in str_repr

    def test_history_ordering(self):
        """Test that history is ordered by modified_at descending"""
        param = Parameter.objects.create(
            name="Test",
            value_type=Parameter.TYPES.STR,
            value="v1",
            enable_history=True,
        )

        param.set_str("v2")
        param.set_str("v3")

        history_list = list(param.history.all())
        # First should be most recent (v2 -> v3)
        assert history_list[0].value == "v2"
        assert history_list[1].value == "v1"

    def test_history_from_dict_preserves_enable_history(self):
        """Test that from_dict preserves enable_history setting"""
        param = Parameter.objects.create(
            name="Test",
            value_type=Parameter.TYPES.STR,
            value="v1",
        )

        param_data = {
            "name": "Test",
            "slug": "TEST",
            "value": "v2",
            "value_type": "STR",
            "description": "",
            "is_global": False,
            "enable_cypher": False,
            "enable_history": True,
        }

        param.from_dict(param_data)
        assert param.enable_history is True

    def test_history_to_dict_includes_enable_history(self):
        """Test that to_dict includes enable_history field"""
        param = Parameter.objects.create(
            name="Test",
            value_type=Parameter.TYPES.STR,
            value="v1",
            enable_history=True,
        )

        param_dict = param.to_dict()
        assert "enable_history" in param_dict
        assert param_dict["enable_history"] is True

    def test_history_to_dict_does_not_export_history_entries(self):
        """Test that to_dict does NOT export history entries"""
        param = Parameter.objects.create(
            name="Test",
            value_type=Parameter.TYPES.STR,
            value="v1",
            enable_history=True,
        )

        param.set_str("v2")
        param.set_str("v3")

        # Should have history
        assert param.history.count() == 2

        # But to_dict should not include it
        param_dict = param.to_dict()
        assert "history" not in param_dict
