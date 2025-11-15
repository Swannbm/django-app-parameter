"""Tests for backward compatibility of dump/load format across versions"""

import json

import pytest
from django.core.management import call_command

from django_app_parameter.models import Parameter


@pytest.mark.django_db
class TestVersionCompatibility:
    """Test that newer versions can load dumps from older versions"""

    def test_load_v1_format_pre_validators(self):
        """Test loading format from v1.x (before validators, before v2.0.0)

        Format: Only basic fields (name, slug, value, value_type, description,
        is_global). No validators, no enable_cypher, no enable_history
        """
        # Simulate a dump from v1.x
        v1_data = json.dumps(
            [
                {
                    "name": "App Name",
                    "slug": "APP_NAME",
                    "value": "MyApp",
                    "value_type": "STR",
                    "description": "Application name",
                    "is_global": True,
                },
                {
                    "name": "Max Users",
                    "slug": "MAX_USERS",
                    "value": "100",
                    "value_type": "INT",
                    "description": "",
                    "is_global": False,
                },
            ]
        )

        # Should load without errors
        call_command("dap_load", json=v1_data)

        # Verify data loaded correctly
        param1 = Parameter.objects.get(slug="APP_NAME")
        assert param1.name == "App Name"
        assert param1.value == "MyApp"
        assert param1.value_type == "STR"
        assert param1.description == "Application name"
        assert param1.is_global is True
        # New fields should have default values
        assert param1.enable_cypher is False
        assert param1.enable_history is False
        assert param1.validators.count() == 0  # type: ignore[attr-defined]

        param2 = Parameter.objects.get(slug="MAX_USERS")
        assert param2.value == "100"
        assert param2.enable_cypher is False
        assert param2.enable_history is False

    def test_load_v2_0_format_with_validators_and_cypher(self):
        """Test loading format from v2.0.0 (with validators and enable_cypher)

        Format: Basic fields + validators + enable_cypher
        No enable_history yet (added in v2.1)
        """
        # Simulate a dump from v2.0.0
        v2_0_data = json.dumps(
            [
                {
                    "name": "Port Number",
                    "slug": "PORT_NUMBER",
                    "value": "8080",
                    "value_type": "INT",
                    "description": "Server port",
                    "is_global": False,
                    "enable_cypher": False,
                    "validators": [
                        {
                            "validator_type": "MinValueValidator",
                            "validator_params": {"limit_value": 1024},
                        },
                        {
                            "validator_type": "MaxValueValidator",
                            "validator_params": {"limit_value": 65535},
                        },
                    ],
                },
                {
                    "name": "Secret Key",
                    "slug": "SECRET_KEY",
                    "value": "my-secret-key",
                    "value_type": "STR",
                    "description": "Application secret",
                    "is_global": True,
                    "enable_cypher": True,
                },
            ]
        )

        # Should load without errors
        call_command("dap_load", json=v2_0_data)

        # Verify data loaded correctly with validators
        port_param = Parameter.objects.get(slug="PORT_NUMBER")
        assert port_param.value == "8080"
        assert port_param.enable_cypher is False
        assert port_param.enable_history is False  # Default value for new field
        assert port_param.validators.count() == 2  # type: ignore[attr-defined]

        validators = list(port_param.validators.all())  # type: ignore[attr-defined]
        assert validators[0].validator_type == "MinValueValidator"  # type: ignore[attr-defined]
        assert validators[0].validator_params == {"limit_value": 1024}  # type: ignore[attr-defined]
        assert validators[1].validator_type == "MaxValueValidator"  # type: ignore[attr-defined]
        assert validators[1].validator_params == {"limit_value": 65535}  # type: ignore[attr-defined]

        # Verify enable_cypher is preserved
        secret_param = Parameter.objects.get(slug="SECRET_KEY")
        assert secret_param.enable_cypher is True
        assert secret_param.enable_history is False  # Default value

    def test_load_v2_1_format_with_history(self):
        """Test loading format from v2.1.0+ (with enable_history)

        Format: All fields including enable_history
        This is the current/complete format
        """
        # Current format with all fields
        v2_1_data = json.dumps(
            [
                {
                    "name": "Database URL",
                    "slug": "DATABASE_URL",
                    "value": "postgresql://localhost/mydb",
                    "value_type": "STR",
                    "description": "Database connection string",
                    "is_global": True,
                    "enable_cypher": True,
                    "enable_history": True,
                    "validators": [
                        {
                            "validator_type": "URLValidator",
                            "validator_params": {},
                        }
                    ],
                },
                {
                    "name": "Max Retries",
                    "slug": "MAX_RETRIES",
                    "value": "3",
                    "value_type": "INT",
                    "description": "Maximum retry attempts",
                    "is_global": False,
                    "enable_cypher": False,
                    "enable_history": True,
                },
            ]
        )

        # Should load without errors
        call_command("dap_load", json=v2_1_data)

        # Verify all fields loaded correctly
        db_param = Parameter.objects.get(slug="DATABASE_URL")
        assert db_param.value == "postgresql://localhost/mydb"
        assert db_param.enable_cypher is True
        assert db_param.enable_history is True
        assert db_param.validators.count() == 1  # type: ignore[attr-defined]

        retry_param = Parameter.objects.get(slug="MAX_RETRIES")
        assert retry_param.value == "3"
        assert retry_param.enable_cypher is False
        assert retry_param.enable_history is True

    def test_dump_v2_1_includes_all_fields(self):
        """Test that current dump (v2.1) includes all fields"""
        # Create a parameter with all features
        # (but not enable_cypher to avoid key issues)
        param = Parameter.objects.create(
            name="Test Param",
            slug="TEST_PARAM",
            value="test_value",
            value_type=Parameter.TYPES.STR,
            description="Test parameter",
            is_global=True,
            enable_cypher=False,
            enable_history=True,
        )

        # Add a validator
        from django_app_parameter.models import ParameterValidator

        ParameterValidator.objects.create(
            parameter=param,
            validator_type="MinLengthValidator",
            validator_params={"limit_value": 5},
        )

        # Export to dict (used by dump command)
        exported = param.to_dict()

        # Verify all expected fields are present
        assert "name" in exported
        assert "slug" in exported
        assert "value" in exported
        assert "value_type" in exported
        assert "description" in exported
        assert "is_global" in exported
        assert "enable_cypher" in exported
        assert "enable_history" in exported
        assert "validators" in exported

        # Verify values are correct
        assert exported["name"] == "Test Param"
        assert exported["enable_cypher"] is False
        assert exported["enable_history"] is True
        assert len(exported["validators"]) == 1

        # Verify history entries are NOT exported
        assert "history" not in exported

    def test_mixed_version_formats_in_single_load(self):
        """Test loading a JSON with mixed format versions (edge case)

        This could happen if someone manually merged dumps from different versions
        """
        mixed_data = json.dumps(
            [
                # v1 format (minimal fields)
                {
                    "name": "Old Param",
                    "slug": "OLD_PARAM",
                    "value": "old",
                    "value_type": "STR",
                    "description": "",
                    "is_global": False,
                },
                # v2.0 format (with enable_cypher, no enable_history)
                {
                    "name": "Middle Param",
                    "slug": "MIDDLE_PARAM",
                    "value": "middle",
                    "value_type": "STR",
                    "description": "",
                    "is_global": False,
                    "enable_cypher": True,
                },
                # v2.1 format (complete)
                {
                    "name": "New Param",
                    "slug": "NEW_PARAM",
                    "value": "new",
                    "value_type": "STR",
                    "description": "",
                    "is_global": False,
                    "enable_cypher": False,
                    "enable_history": True,
                },
            ]
        )

        # Should handle all formats gracefully
        call_command("dap_load", json=mixed_data)

        # Verify each parameter loaded with appropriate defaults
        old = Parameter.objects.get(slug="OLD_PARAM")
        assert old.enable_cypher is False
        assert old.enable_history is False

        middle = Parameter.objects.get(slug="MIDDLE_PARAM")
        assert middle.enable_cypher is True
        assert middle.enable_history is False  # Default

        new = Parameter.objects.get(slug="NEW_PARAM")
        assert new.enable_cypher is False
        assert new.enable_history is True

    def test_load_preserves_enable_cypher_false_explicitly(self):
        """Test that enable_cypher=False is preserved (not just defaulted)

        This ensures we distinguish between:
        - Missing field (old version) -> defaults to False
        - Explicit False (v2.0+) -> preserved as False
        """
        data = json.dumps(
            [
                {
                    "name": "Explicitly Not Encrypted",
                    "slug": "NOT_ENCRYPTED",
                    "value": "plain_text",
                    "value_type": "STR",
                    "description": "",
                    "is_global": False,
                    "enable_cypher": False,  # Explicitly set to False
                }
            ]
        )

        call_command("dap_load", json=data)

        param = Parameter.objects.get(slug="NOT_ENCRYPTED")
        assert param.enable_cypher is False

        # If we update it, it should stay False
        param.value = "new_value"
        param.save()
        param.refresh_from_db()
        assert param.enable_cypher is False

    def test_load_preserves_enable_history_false_explicitly(self):
        """Test that enable_history=False is preserved (not just defaulted)"""
        data = json.dumps(
            [
                {
                    "name": "No History Tracking",
                    "slug": "NO_HISTORY",
                    "value": "value",
                    "value_type": "STR",
                    "description": "",
                    "is_global": False,
                    "enable_cypher": False,
                    "enable_history": False,  # Explicitly set to False
                }
            ]
        )

        call_command("dap_load", json=data)

        param = Parameter.objects.get(slug="NO_HISTORY")
        assert param.enable_history is False

        # Modify value - should not create history
        param.set_str("new_value")
        assert param.history.count() == 0  # type: ignore[attr-defined]
