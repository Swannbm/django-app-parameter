"""Tests for encryption functionality."""

import pytest
from cryptography.fernet import Fernet
from django.core.exceptions import ImproperlyConfigured

from django_app_parameter.models import Parameter
from django_app_parameter.utils import decrypt_value, encrypt_value, get_encryption_key


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


class TestEncryptionUtilities:
    """Tests for encryption utility functions."""

    def test_get_encryption_key_from_settings(
        self, configure_encryption, encryption_key
    ):
        """Test retrieval of encryption key from settings."""
        key = get_encryption_key()
        assert key == encryption_key.encode("utf-8")

    def test_get_encryption_key_with_custom_key(self):
        """Test get_encryption_key with custom key parameter."""
        custom_key = Fernet.generate_key().decode("utf-8")
        key = get_encryption_key(custom_key)
        assert key == custom_key.encode("utf-8")

    def test_get_encryption_key_not_configured(self, settings):
        """Test error when key is not configured."""
        if hasattr(settings, "DJANGO_APP_PARAMETER"):
            settings.DJANGO_APP_PARAMETER.pop("encryption_key", None)

        with pytest.raises(ImproperlyConfigured) as exc_info:
            get_encryption_key()
        assert "No encryption key configured" in str(exc_info.value)

    def test_encrypt_decrypt_roundtrip(self, configure_encryption):
        """Test encryption and decryption roundtrip."""
        original = "secret_value_123"
        encrypted = encrypt_value(original)
        decrypted = decrypt_value(encrypted)
        assert decrypted == original
        assert encrypted != original

    def test_encrypt_decrypt_with_custom_key(self, configure_encryption):
        """Test encryption with custom key."""
        custom_key = Fernet.generate_key().decode("utf-8")
        original = "test_value"

        encrypted = encrypt_value(original, encryption_key=custom_key)
        decrypted = decrypt_value(encrypted, encryption_key=custom_key)
        assert decrypted == original

        # Should fail with default key
        from cryptography.fernet import InvalidToken

        with pytest.raises(InvalidToken):
            decrypt_value(encrypted)


class TestParameterEncryption:
    """Tests for parameter encryption functionality."""

    def test_set_and_get_encrypted_value(self, db, configure_encryption):
        """Test basic set/get with encryption."""
        param = Parameter.objects.create(
            name="Secret",
            value_type=Parameter.TYPES.STR,
            value="initial",
            enable_cypher=True,
        )

        param.set_str("secret_value")
        param.refresh_from_db()

        # Value encrypted in DB
        assert param.value.startswith("gAAAAA")
        # But decrypted when read
        assert param.str() == "secret_value"

    def test_encryption_with_different_types(self, db, configure_encryption):
        """Test encryption works with different parameter types."""
        test_cases = [
            (Parameter.TYPES.STR, "test", "set_str"),
            (Parameter.TYPES.INT, 42, "set_int"),
            (Parameter.TYPES.FLT, 3.14, "set_float"),
            (Parameter.TYPES.BOO, True, "set_bool"),
        ]

        for value_type, test_value, setter in test_cases:
            param = Parameter.objects.create(
                name=f"Test {value_type}",
                value_type=value_type,
                value="0",
                enable_cypher=True,
            )
            getattr(param, setter)(test_value)
            param.refresh_from_db()

            assert param.value.startswith("gAAAAA")
            assert param.get() == test_value

    def test_enable_encryption_on_existing_parameter(self, db, configure_encryption):
        """Test enabling encryption on existing parameter."""
        param = Parameter.objects.create(
            name="Secret",
            value_type=Parameter.TYPES.STR,
            value="plain",
            enable_cypher=False,
        )

        # Enable encryption
        param.enable_cypher = True
        param.set_str("new_value")
        param.refresh_from_db()

        assert param.value.startswith("gAAAAA")
        assert param.str() == "new_value"

    def test_to_dict_exports_decrypted_value(self, db, configure_encryption):
        """Test to_dict exports decrypted values."""
        param = Parameter.objects.create(
            name="Secret",
            value_type=Parameter.TYPES.STR,
            value="test",
            enable_cypher=True,
        )
        param.set_str("secret")
        param.refresh_from_db()

        param_dict = param.to_dict()
        assert param_dict["value"] == "secret"

    def test_validators_work_with_encryption(self, db, configure_encryption):
        """Test validators work with encrypted parameters."""
        from django.core.exceptions import ValidationError

        param = Parameter.objects.create(
            name="Age",
            value_type=Parameter.TYPES.INT,
            value="25",
            enable_cypher=True,
        )
        param.validators.create(
            validator_type="MaxValueValidator", validator_params={"limit_value": 100}
        )

        param.set_int(50)
        assert param.int() == 50

        with pytest.raises(ValidationError):
            param.set_int(150)


class TestEncryptionEdgeCases:
    """Tests for edge cases in encryption."""

    def test_empty_string_encryption(self, db, configure_encryption):
        """Test encrypting empty string."""
        param = Parameter.objects.create(
            name="Empty",
            value_type=Parameter.TYPES.STR,
            value="",
            enable_cypher=True,
        )

        param.set_str("")
        param.refresh_from_db()

        assert param.value.startswith("gAAAAA")
        assert param.str() == ""

    def test_special_characters_encryption(self, db, configure_encryption):
        """Test encrypting strings with special characters."""
        special_string = "Hello! @#$%^&*() 你好 🎉"

        param = Parameter.objects.create(
            name="Special",
            value_type=Parameter.TYPES.STR,
            value="test",
            enable_cypher=True,
        )

        param.set_str(special_string)
        param.refresh_from_db()

        assert param.value.startswith("gAAAAA")
        assert param.str() == special_string
