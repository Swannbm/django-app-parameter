"""Tests for encryption functionality when cryptography is not installed."""

from unittest.mock import patch

import pytest
from django.core.exceptions import ImproperlyConfigured


class TestEncryptionWithoutCryptography:
    """Test encryption utilities when cryptography package is not available."""

    def test_get_encryption_key_without_cryptography(self):
        """Test that get_encryption_key raises ImproperlyConfigured without cryptography."""
        # Mock HAS_CRYPTOGRAPHY to False
        with patch("django_app_parameter.utils.HAS_CRYPTOGRAPHY", False):
            from django_app_parameter.utils import get_encryption_key

            with pytest.raises(ImproperlyConfigured) as exc_info:
                get_encryption_key()
            assert "cryptography" in str(exc_info.value).lower()
