"""Command to rotate encryption key for encrypted parameters.

Two-step process for secure key rotation:

Step 1: Generate new key and backup old one
    python manage.py dap_rotate_key
    - Backs up current key to dap_backup_key.json
    - Generates and displays new key
    - Shows next command to run

Step 2: Apply rotation with old key
    python manage.py dap_rotate_key --old-key <key>
    - Decrypts with old key (from parameter)
    - Re-encrypts with new key (from settings)

Arguments:
    --old-key: Old encryption key for decryption. When provided, performs step 2.
    --backup-file: Path to backup file (default: dap_backup_key.json at project root)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandParser

from django_app_parameter.models import Parameter
from django_app_parameter.utils import decrypt_value, encrypt_value, get_setting

if TYPE_CHECKING:
    from typing_extensions import TypedDict

    class KeyBackupEntry(TypedDict):
        """Structure for a single key backup entry."""

        timestamp: str
        key: str
        parameters_count: int

    class BackupData(TypedDict):
        """Structure for the backup file."""

        keys: list[KeyBackupEntry]


try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:
    Fernet = None  # type: ignore[assignment, misc]
    InvalidToken = None  # type: ignore[assignment, misc]

HAS_CRYPTOGRAPHY = Fernet is not None

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Rotate encryption key for encrypted parameters (two-step process)"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--old-key",
            type=str,
            help="Old encryption key for decryption (triggers step 2: apply rotation)",
        )
        parser.add_argument(
            "--backup-file",
            type=str,
            help="Path to backup file (default: dap_backup_key.json at project root)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        # Check if cryptography is available
        if not HAS_CRYPTOGRAPHY:
            raise ImproperlyConfigured(
                "Encryption requires the 'cryptography' package. "
                "Install it with: pip install django-app-parameter[cryptography]"
            )

        # Determine backup file location
        backup_file_path = self._get_backup_file_path(options.get("backup_file"))

        if options.get("old_key"):
            # Step 2: Apply rotation
            self._apply_rotation(options["old_key"], backup_file_path)
        else:
            # Step 1: Generate new key and backup
            self._generate_and_backup(backup_file_path)

    def _get_backup_file_path(self, custom_path: str | None) -> Path:
        """Get the backup file path from settings or parameter."""
        if custom_path:
            return Path(custom_path)

        # Try to get from settings
        backup_path = get_setting("encryption_key_backup_file")
        if backup_path:
            return Path(backup_path)

        # Default to project root
        return Path("dap_backup_key.json")

    def _generate_and_backup(self, backup_file: Path) -> None:
        """Step 1: Generate new key and backup the old one."""
        self.stdout.write(
            self.style.HTTP_INFO("=== Step 1: Generate new key and backup ===\n")
        )

        # Get current key from settings
        try:
            current_key_str = get_setting("encryption_key")
            if not current_key_str:
                self.stdout.write(
                    self.style.ERROR(
                        "No encryption key configured in settings. Nothing to rotate."
                    )
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to get current encryption key: {e}")
            )
            return

        # Check if there are encrypted parameters
        encrypted_count = Parameter.objects.filter(enable_cypher=True).count()
        self.stdout.write(f"Found {encrypted_count} encrypted parameters\n")

        # Generate new key
        new_key = Fernet.generate_key()  # type: ignore[misc]
        new_key_str = new_key.decode("utf-8")

        # Backup old key with timestamp
        timestamp = datetime.now().isoformat()

        # Load existing backup file or create new structure
        backup_data: dict[str, Any]
        if backup_file.exists():
            with backup_file.open("r") as f:
                backup_data = json.load(f)
        else:
            backup_data = {"keys": []}

        # Add current key to backup history
        backup_data["keys"].append(
            {
                "timestamp": timestamp,
                "key": current_key_str,
                "parameters_count": encrypted_count,
            }
        )

        # Write backup file
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        with backup_file.open("w") as f:
            json.dump(backup_data, f, indent=4)

        self.stdout.write(self.style.SUCCESS(f"✓ Backed up old key to: {backup_file}"))
        self.stdout.write(self.style.SUCCESS("✓ Generated new encryption key\n"))

        # Display new key
        self.stdout.write(self.style.HTTP_INFO("NEW ENCRYPTION KEY:"))
        self.stdout.write(self.style.WARNING(f"{new_key_str}\n"))

        # Display instructions
        self.stdout.write(self.style.HTTP_INFO("NEXT STEPS:"))
        self.stdout.write(
            "1. Update your settings with the new key:\n"
            f"   DJANGO_APP_PARAMETER = {{'encryption_key': '{new_key_str}'}}\n"
        )
        self.stdout.write("2. Restart your application to use the new key\n")
        self.stdout.write(
            "3. Once settings are updated, run:\n"
            f"   python manage.py dap_rotate_key --old-key {current_key_str}\n"
        )

    def _apply_rotation(self, old_key_str: str, backup_file: Path) -> None:
        """Step 2: Re-encrypt parameters with new key from settings."""
        self.stdout.write(self.style.HTTP_INFO("=== Step 2: Apply rotation ===\n"))

        # Validate old key
        try:
            old_key = old_key_str.encode("utf-8")
            Fernet(old_key)  # type: ignore[misc]  # Validate Fernet key format
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Invalid old key provided: {e}"))
            return

        # Get new key from settings
        try:
            new_key_str = get_setting("encryption_key")
            if not new_key_str:
                self.stdout.write(
                    self.style.ERROR(
                        "No encryption key configured in settings. "
                        "Please update settings first."
                    )
                )
                return
            new_key = new_key_str.encode("utf-8")
            Fernet(new_key)  # type: ignore[misc]  # Validate
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Invalid encryption key in settings: {e}")
            )
            return

        # Check if old and new keys are the same
        if old_key_str == new_key_str:
            self.stdout.write(
                self.style.ERROR(
                    "Old key and new key are identical. "
                    "Please update settings with the new key first."
                )
            )
            return

        # Get encrypted parameters
        encrypted_params = Parameter.objects.filter(enable_cypher=True)
        count = encrypted_params.count()

        if count == 0:
            self.stdout.write(
                self.style.WARNING("No encrypted parameters found. Nothing to do.")
            )
            return

        self.stdout.write(f"Processing {count} encrypted parameters...\n")

        # Re-encrypt each parameter using helpers with explicit keys
        success_count = 0
        failed_params: list[str] = []

        for param in encrypted_params:
            try:
                # Decrypt with old key (passing key explicitly)
                decrypted_value = decrypt_value(param.value, encryption_key=old_key_str)

                # Re-encrypt with new key (passing key explicitly)
                param.value = encrypt_value(decrypted_value, encryption_key=new_key_str)
                param.save()

                success_count += 1
                logger.debug("Re-encrypted parameter: %s", param.slug)

            except InvalidToken:  # type: ignore[misc]
                failed_params.append(f"{param.slug} (failed to decrypt with old key)")
                logger.error("Failed to decrypt parameter %s with old key", param.slug)
            except Exception as e:
                failed_params.append(f"{param.slug} ({e})")
                logger.error("Failed to re-encrypt parameter %s: %s", param.slug, e)

        # Display results
        if success_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ Successfully re-encrypted {success_count}/{count} parameters"
                )
            )

        if failed_params:
            self.stdout.write(
                self.style.ERROR(
                    f"\n✗ Failed to re-encrypt {len(failed_params)} parameters:"
                )
            )
            for failed in failed_params:
                self.stdout.write(f"  - {failed}")
            self.stdout.write(
                self.style.WARNING(f"\nCheck backup file for recovery: {backup_file}")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("\n✓ Rotation completed successfully!")
            )
            self.stdout.write(f"Backup file available at: {backup_file}")
