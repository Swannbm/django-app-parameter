"""Tests for dap_rotate_key management command."""

import json
from io import StringIO
from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from django.core.management import call_command

from django_app_parameter.models import Parameter


@pytest.fixture
def encryption_key():
    """Generate a test encryption key."""
    return Fernet.generate_key().decode("utf-8")


@pytest.fixture
def configure_encryption(settings, encryption_key):
    """Configure encryption key in settings."""
    if not hasattr(settings, "DJANGO_APP_PARAMETER"):
        settings.DJANGO_APP_PARAMETER = {}
    settings.DJANGO_APP_PARAMETER["encryption_key"] = encryption_key
    return encryption_key


class TestRotateKeyCommandStep1:
    """Tests for step 1: generate new key and backup."""

    def test_step1_with_no_key_configured(self, db, tmp_path):
        """Test step 1 when no encryption key is configured."""
        backup_file = tmp_path / "backup.json"

        out = StringIO()
        call_command("dap_rotate_key", backup_file=str(backup_file), stdout=out)
        output = out.getvalue()

        assert "No encryption key configured" in output
        assert not backup_file.exists()

    def test_step1_generates_key_and_backup(self, db, configure_encryption, tmp_path):
        """Test step 1: generate new key and backup old one."""
        # Create encrypted parameter
        param = Parameter.objects.create(
            name="Secret",
            value_type=Parameter.TYPES.STR,
            value="test",
            enable_cypher=True,
        )
        param.set_str("secret_value")

        backup_file = tmp_path / "backup.json"
        old_key = configure_encryption

        # Step 1: Generate new key
        out = StringIO()
        call_command("dap_rotate_key", backup_file=str(backup_file), stdout=out)
        output = out.getvalue()

        # Check output
        assert "Step 1" in output
        assert "Found 1 encrypted parameters" in output
        assert "NEW ENCRYPTION KEY:" in output
        assert "NEXT STEPS:" in output
        assert "dap_rotate_key --old-key" in output

        # Check backup file was created
        assert backup_file.exists()

        with backup_file.open() as f:
            backup_data = json.load(f)

        assert "keys" in backup_data
        assert len(backup_data["keys"]) == 1
        assert backup_data["keys"][0]["key"] == old_key
        assert backup_data["keys"][0]["parameters_count"] == 1
        assert "timestamp" in backup_data["keys"][0]

    def test_step1_appends_to_existing_backup(self, db, configure_encryption, tmp_path):
        """Test that step 1 appends to existing backup file."""
        backup_file = tmp_path / "backup.json"

        # Create initial backup
        initial_data = {
            "keys": [
                {
                    "timestamp": "2024-01-01T00:00:00",
                    "key": "old_key_1",
                    "parameters_count": 5,
                }
            ]
        }
        with backup_file.open("w") as f:
            json.dump(initial_data, f)

        # Run step 1
        out = StringIO()
        call_command("dap_rotate_key", backup_file=str(backup_file), stdout=out)

        # Check backup was appended
        with backup_file.open() as f:
            backup_data = json.load(f)

        assert len(backup_data["keys"]) == 2
        assert backup_data["keys"][0]["key"] == "old_key_1"
        assert backup_data["keys"][1]["key"] == configure_encryption


class TestRotateKeyCommandStep2:
    """Tests for step 2: apply rotation."""

    def test_step2_with_no_encrypted_parameters(
        self, db, configure_encryption, tmp_path
    ):
        """Test step 2 with no encrypted parameters."""
        old_key = Fernet.generate_key().decode("utf-8")
        backup_file = tmp_path / "backup.json"

        out = StringIO()
        call_command(
            "dap_rotate_key",
            old_key=old_key,
            backup_file=str(backup_file),
            stdout=out,
        )
        output = out.getvalue()

        assert "No encrypted parameters found" in output

    def test_step2_successful_rotation(
        self, db, configure_encryption, tmp_path, settings
    ):
        """Test step 2: successful rotation."""
        # Create encrypted parameters with old key
        old_key = configure_encryption
        param1 = Parameter.objects.create(
            name="Secret1",
            value_type=Parameter.TYPES.STR,
            value="test1",
            enable_cypher=True,
        )
        param1.set_str("value1")

        param2 = Parameter.objects.create(
            name="Secret2",
            value_type=Parameter.TYPES.INT,
            value="10",
            enable_cypher=True,
        )
        param2.set_int(42)

        # Generate and configure new key in settings
        new_key = Fernet.generate_key().decode("utf-8")
        settings.DJANGO_APP_PARAMETER["encryption_key"] = new_key

        backup_file = tmp_path / "backup.json"

        # Step 2: Apply rotation
        out = StringIO()
        call_command(
            "dap_rotate_key",
            old_key=old_key,
            backup_file=str(backup_file),
            stdout=out,
        )
        output = out.getvalue()

        # Check output
        assert "Step 2" in output
        assert "Processing 2 encrypted parameters" in output
        assert "Successfully re-encrypted 2/2 parameters" in output
        assert "Rotation completed successfully" in output

        # Verify parameters were re-encrypted
        param1.refresh_from_db()
        param2.refresh_from_db()

        # Values should still be encrypted (starts with Fernet prefix)
        assert param1.value.startswith("gAAAAA")
        assert param2.value.startswith("gAAAAA")

        # Should be able to decrypt with new key
        assert param1.str() == "value1"
        assert param2.int() == 42

    def test_step2_with_invalid_old_key(self, db, configure_encryption, tmp_path):
        """Test step 2 with invalid old key."""
        # Create encrypted parameter
        param = Parameter.objects.create(
            name="Secret",
            value_type=Parameter.TYPES.STR,
            value="test",
            enable_cypher=True,
        )
        param.set_str("value")

        # Try with invalid old key
        backup_file = tmp_path / "backup.json"
        out = StringIO()
        call_command(
            "dap_rotate_key",
            old_key="invalid_key",
            backup_file=str(backup_file),
            stdout=out,
        )
        output = out.getvalue()

        assert "Invalid old key provided" in output

    def test_step2_with_same_old_and_new_key(self, db, configure_encryption, tmp_path):
        """Test step 2 when old and new keys are identical."""
        old_key = configure_encryption
        backup_file = tmp_path / "backup.json"

        out = StringIO()
        call_command(
            "dap_rotate_key",
            old_key=old_key,
            backup_file=str(backup_file),
            stdout=out,
        )
        output = out.getvalue()

        assert "Old key and new key are identical" in output

    def test_step2_with_decryption_failure(
        self, db, configure_encryption, tmp_path, settings
    ):
        """Test step 2 when decryption fails."""
        # Create encrypted parameter
        param = Parameter.objects.create(
            name="Secret",
            value_type=Parameter.TYPES.STR,
            value="test",
            enable_cypher=True,
        )
        param.set_str("value")

        # Use wrong old key
        wrong_old_key = Fernet.generate_key().decode("utf-8")

        # Set new key in settings
        new_key = Fernet.generate_key().decode("utf-8")
        settings.DJANGO_APP_PARAMETER["encryption_key"] = new_key

        backup_file = tmp_path / "backup.json"

        # Step 2 with wrong old key
        out = StringIO()
        call_command(
            "dap_rotate_key",
            old_key=wrong_old_key,
            backup_file=str(backup_file),
            stdout=out,
        )
        output = out.getvalue()

        # Should show failure
        assert "Failed to re-encrypt 1 parameters" in output
        assert "failed to decrypt with old key" in output


class TestRotateKeyCommandBackupFile:
    """Tests for backup file handling."""

    def test_default_backup_location(self, db, configure_encryption):
        """Test default backup file location."""
        default_backup = Path("dap_backup_key.json")

        # Clean up if exists
        if default_backup.exists():
            default_backup.unlink()

        # Run step 1 without backup_file option
        out = StringIO()
        call_command("dap_rotate_key", stdout=out)

        # Check default backup file was created
        assert default_backup.exists()

        # Clean up
        default_backup.unlink()

    def test_custom_backup_location_from_settings(
        self, db, configure_encryption, tmp_path, settings
    ):
        """Test custom backup location from settings."""
        custom_backup = tmp_path / "custom_backup.json"
        settings.DJANGO_APP_PARAMETER["encryption_key_backup_file"] = str(custom_backup)

        # Run step 1
        out = StringIO()
        call_command("dap_rotate_key", stdout=out)

        # Check custom backup file was created
        assert custom_backup.exists()
