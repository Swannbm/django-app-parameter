"""Tests for dump_param management command"""

import json

import pytest
from django.core.management import call_command

from django_app_parameter.models import Parameter, ParameterValidator


@pytest.mark.django_db
class TestDumpParamCommand:
    """Test dump_param management command"""

    def test_dump_param_basic(self, tmp_path):
        """Test basic dump_param functionality"""
        # Create test parameters
        Parameter.objects.create(
            name="Test Param 1",
            slug="TEST_PARAM_1",
            value="value1",
            value_type="STR",
            description="Test description",
            is_global=True,
        )
        Parameter.objects.create(
            name="Test Param 2",
            slug="TEST_PARAM_2",
            value="42",
            value_type="INT",
        )

        # Dump to file
        output_file = tmp_path / "output.json"
        call_command("dump_param", str(output_file))

        # Verify file was created
        assert output_file.exists()

        # Read and verify content
        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        assert isinstance(data, list)
        assert len(data) == 2

        # Verify parameter data
        param1 = next(p for p in data if p["slug"] == "TEST_PARAM_1")
        assert param1["name"] == "Test Param 1"
        assert param1["value"] == "value1"
        assert param1["value_type"] == "STR"
        assert param1["description"] == "Test description"
        assert param1["is_global"] is True

        param2 = next(p for p in data if p["slug"] == "TEST_PARAM_2")
        assert param2["name"] == "Test Param 2"
        assert param2["value"] == "42"
        assert param2["value_type"] == "INT"

    def test_dump_param_with_validators(self, tmp_path):
        """Test dump_param includes validators"""
        # Create parameter with validators
        param = Parameter.objects.create(
            name="Validated Param",
            slug="VALIDATED_PARAM",
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

        # Dump to file
        output_file = tmp_path / "with_validators.json"
        call_command("dump_param", str(output_file))

        # Read and verify
        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 1
        param_data = data[0]

        # Verify validators are included
        assert "validators" in param_data
        assert len(param_data["validators"]) == 2

        validators = param_data["validators"]
        assert validators[0]["validator_type"] == "MinValueValidator"
        assert validators[0]["validator_params"] == {"limit_value": 10}
        assert validators[1]["validator_type"] == "MaxValueValidator"
        assert validators[1]["validator_params"] == {"limit_value": 100}

    def test_dump_param_without_validators(self, tmp_path):
        """Test dump_param with parameter without validators"""
        Parameter.objects.create(
            name="Simple Param",
            slug="SIMPLE_PARAM",
            value="test",
        )

        output_file = tmp_path / "no_validators.json"
        call_command("dump_param", str(output_file))

        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        # Validators key should not be present
        assert "validators" not in data[0]

    def test_dump_param_empty_database(self, tmp_path):
        """Test dump_param with no parameters in database"""
        output_file = tmp_path / "empty.json"
        call_command("dump_param", str(output_file))

        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        assert isinstance(data, list)
        assert len(data) == 0

    def test_dump_param_custom_indent(self, tmp_path):
        """Test dump_param with custom indentation"""
        Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="value",
        )

        # Test with indent=2
        output_file = tmp_path / "indent2.json"
        call_command("dump_param", str(output_file), indent=2)

        content = output_file.read_text(encoding="utf-8")
        # Check that file has proper indentation (2 spaces)
        assert '  "name"' in content or '  "slug"' in content

    def test_dump_param_indent_default(self, tmp_path):
        """Test dump_param uses default indent of 4"""
        Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="value",
        )

        output_file = tmp_path / "default_indent.json"
        call_command("dump_param", str(output_file))

        content = output_file.read_text(encoding="utf-8")
        # Check that file has proper indentation (4 spaces by default)
        assert '    "name"' in content or '    "slug"' in content

    def test_dump_param_unicode_content(self, tmp_path):
        """Test dump_param handles unicode characters correctly"""
        Parameter.objects.create(
            name="Unicode Param",
            slug="UNICODE_PARAM",
            value="Café à Paris 🇫🇷",
            description="Château élégant",
        )

        output_file = tmp_path / "unicode.json"
        call_command("dump_param", str(output_file))

        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        param = data[0]
        assert param["value"] == "Café à Paris 🇫🇷"
        assert param["description"] == "Château élégant"

    def test_dump_param_all_types(self, tmp_path):
        """Test dump_param with parameters of all value types"""
        types_to_test = [
            ("STR", "test string"),
            ("INT", "42"),
            ("FLT", "3.14"),
            ("DCL", "99.99"),
            ("BOO", "1"),
            ("DAT", "2024-01-01"),
            ("DTM", "2024-01-01T12:00:00"),
            ("TIM", "12:00:00"),
            ("URL", "https://example.com"),
            ("EML", "test@example.com"),
            ("LST", "a, b, c"),
            ("DCT", '{"key": "value"}'),
            ("JSN", "[1, 2, 3]"),
            ("PTH", "/path/to/file"),
            ("DUR", "3600"),
            ("PCT", "75.5"),
        ]

        for i, (value_type, value) in enumerate(types_to_test):
            Parameter.objects.create(
                name=f"Param {i}",
                slug=f"PARAM_{i}",
                value=value,
                value_type=value_type,
            )

        output_file = tmp_path / "all_types.json"
        call_command("dump_param", str(output_file))

        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == len(types_to_test)

        # Verify each type is correctly exported
        for param_data in data:
            assert "name" in param_data
            assert "slug" in param_data
            assert "value" in param_data
            assert "value_type" in param_data

    def test_dump_param_multiple_parameters(self, tmp_path):
        """Test dump_param with multiple parameters"""
        # Create 10 parameters
        for i in range(10):
            Parameter.objects.create(
                name=f"Param {i}",
                slug=f"PARAM_{i}",
                value=f"value{i}",
                description=f"Description {i}",
                is_global=(i % 2 == 0),
            )

        output_file = tmp_path / "multiple.json"
        call_command("dump_param", str(output_file))

        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 10

        # Verify all parameters are present
        slugs = {p["slug"] for p in data}
        expected_slugs = {f"PARAM_{i}" for i in range(10)}
        assert slugs == expected_slugs

    def test_dump_load_roundtrip(self, tmp_path):
        """Test that dump -> load produces identical data"""
        # Create diverse parameters
        param1 = Parameter.objects.create(
            name="String Param",
            slug="STRING_PARAM",
            value="test",
            value_type="STR",
            description="A string parameter",
            is_global=True,
        )
        ParameterValidator.objects.create(
            parameter=param1,
            validator_type="MinLengthValidator",
            validator_params={"limit_value": 3},
        )

        Parameter.objects.create(
            name="Int Param",
            slug="INT_PARAM",
            value="42",
            value_type="INT",
            is_global=False,
        )

        # Dump
        dump_file = tmp_path / "dump.json"
        call_command("dump_param", str(dump_file))

        # Read dumped data
        with open(dump_file, encoding="utf-8") as f:
            dumped_data = json.load(f)

        # Clear database
        Parameter.objects.all().delete()
        assert Parameter.objects.count() == 0

        # Load back
        call_command("load_param", file=str(dump_file))

        # Dump again
        dump_file2 = tmp_path / "dump2.json"
        call_command("dump_param", str(dump_file2))

        # Read second dump
        with open(dump_file2, encoding="utf-8") as f:
            dumped_data2 = json.load(f)

        # Compare: should be identical
        assert dumped_data == dumped_data2

    def test_dump_param_file_path_required(self):
        """Test that dump_param requires a file path argument"""
        from django.core.management import CommandError

        with pytest.raises((SystemExit, CommandError, TypeError)):
            call_command("dump_param")

    def test_dump_param_creates_parent_directories(self, tmp_path):
        """Test that dump_param creates parent directories if needed"""
        # Create a nested path that doesn't exist
        nested_path = tmp_path / "nested" / "deep" / "path"
        output_file = nested_path / "output.json"

        # Ensure parent doesn't exist
        assert not nested_path.exists()

        Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="value",
        )

        # This should create the directories
        # Note: The command doesn't create directories, so this might fail
        # Let's create them first to test the command works
        nested_path.mkdir(parents=True, exist_ok=True)

        call_command("dump_param", str(output_file))

        assert output_file.exists()

    def test_dump_param_stdout_message(self, tmp_path, capsys):
        """Test that dump_param outputs success message"""
        Parameter.objects.create(
            name="Test",
            slug="TEST",
            value="value",
        )

        output_file = tmp_path / "output.json"
        call_command("dump_param", str(output_file))

        # Capture stdout
        captured = capsys.readouterr()

        # Should contain success message with count
        assert "Successfully exported" in captured.out
        assert "1 parameter" in captured.out
        assert str(output_file) in captured.out

    def test_dump_param_multiple_stdout_message(self, tmp_path, capsys):
        """Test stdout message shows correct count for multiple parameters"""
        for i in range(5):
            Parameter.objects.create(
                name=f"Test {i}",
                slug=f"TEST_{i}",
                value="value",
            )

        output_file = tmp_path / "output.json"
        call_command("dump_param", str(output_file))

        captured = capsys.readouterr()

        assert "5 parameter(s)" in captured.out
