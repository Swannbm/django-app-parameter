"""Unit tests for Parameter model methods: cast and type check."""

from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from django_app_parameter.models import (
    Parameter,
    ParameterBool,
    ParameterDate,
    ParameterDatetime,
    ParameterDecimal,
    ParameterDict,
    ParameterDuration,
    ParameterEmail,
    ParameterFloat,
    ParameterInt,
    ParameterJson,
    ParameterList,
    ParameterPath,
    ParameterPercentage,
    ParameterStr,
    ParameterTime,
    ParameterUrl,
)


class TestParameterCastFromStr:
    """Tests for _cast_from_str method on all parameter types."""

    def test_parameter_str_cast_from_str(self):
        param = ParameterStr(name="test")
        assert param._cast_from_str("hello") == "hello"
        assert param._cast_from_str("  spaced  ") == "  spaced  "
        assert param._cast_from_str("") == ""
        assert param._cast_from_str("123") == "123"

    def test_parameter_int_cast_from_str(self):
        param = ParameterInt(name="test")
        assert param._cast_from_str("42") == 42
        assert param._cast_from_str("-10") == -10
        assert param._cast_from_str("0") == 0

    def test_parameter_int_cast_from_str_invalid(self):
        param = ParameterInt(name="test")
        with pytest.raises(ValueError):
            param._cast_from_str("not_a_number")
        with pytest.raises(ValueError):
            param._cast_from_str("3.14")

    def test_parameter_float_cast_from_str(self):
        param = ParameterFloat(name="test")
        assert param._cast_from_str("3.14") == 3.14
        assert param._cast_from_str("-2.5") == -2.5
        assert param._cast_from_str("0") == 0.0
        assert param._cast_from_str("1e10") == 1e10

    def test_parameter_float_cast_from_str_invalid(self):
        param = ParameterFloat(name="test")
        with pytest.raises(ValueError):
            param._cast_from_str("not_a_float")

    def test_parameter_decimal_cast_from_str(self):
        param = ParameterDecimal(name="test")
        assert param._cast_from_str("3.14159") == Decimal("3.14159")
        assert param._cast_from_str("-100.50") == Decimal("-100.50")
        assert param._cast_from_str("0") == Decimal("0")

    def test_parameter_decimal_cast_from_str_invalid(self):
        param = ParameterDecimal(name="test")
        from decimal import InvalidOperation

        with pytest.raises(InvalidOperation):
            param._cast_from_str("not_decimal")

    def test_parameter_bool_cast_from_str_truthy(self):
        param = ParameterBool(name="test")
        assert param._cast_from_str("1") is True
        assert param._cast_from_str("true") is True
        assert param._cast_from_str("True") is True
        assert param._cast_from_str("yes") is True
        assert param._cast_from_str("anything") is True

    def test_parameter_bool_cast_from_str_falsy(self):
        param = ParameterBool(name="test")
        assert param._cast_from_str("0") is False
        assert param._cast_from_str("false") is False
        assert param._cast_from_str("False") is False
        assert param._cast_from_str("no") is False
        assert param._cast_from_str("off") is False
        assert param._cast_from_str("OFF") is False
        assert param._cast_from_str("") is False

    def test_parameter_date_cast_from_str(self):
        param = ParameterDate(name="test")
        assert param._cast_from_str("2024-03-15") == date(2024, 3, 15)
        assert param._cast_from_str("2000-01-01") == date(2000, 1, 1)
        assert param._cast_from_str("  2024-03-15  ") == date(2024, 3, 15)

    def test_parameter_date_cast_from_str_invalid(self):
        param = ParameterDate(name="test")
        with pytest.raises(ValueError):
            param._cast_from_str("not-a-date")
        with pytest.raises(ValueError):
            param._cast_from_str("15/03/2024")

    def test_parameter_datetime_cast_from_str(self):
        param = ParameterDatetime(name="test")
        assert param._cast_from_str("2024-03-15T14:30:00") == datetime(
            2024, 3, 15, 14, 30, 0
        )
        assert param._cast_from_str("2024-03-15T00:00:00") == datetime(
            2024, 3, 15, 0, 0, 0
        )
        assert param._cast_from_str("  2024-03-15T14:30:00  ") == datetime(
            2024, 3, 15, 14, 30, 0
        )

    def test_parameter_datetime_cast_from_str_invalid(self):
        param = ParameterDatetime(name="test")
        with pytest.raises(ValueError):
            param._cast_from_str("not-a-datetime")

    def test_parameter_time_cast_from_str(self):
        param = ParameterTime(name="test")
        assert param._cast_from_str("14:30:00") == time(14, 30, 0)
        assert param._cast_from_str("00:00:00") == time(0, 0, 0)
        assert param._cast_from_str("23:59:59") == time(23, 59, 59)
        assert param._cast_from_str("  14:30:00  ") == time(14, 30, 0)

    def test_parameter_time_cast_from_str_already_time(self):
        """Test that _cast_from_str returns time object unchanged if already a time."""
        param = ParameterTime(name="test")
        time_value = time(14, 30, 0)
        # Note: implementation accepts time objects despite str type hint
        assert param._cast_from_str(time_value) is time_value  # type: ignore[arg-type]

    def test_parameter_time_cast_from_str_invalid(self):
        param = ParameterTime(name="test")
        with pytest.raises(ValueError):
            param._cast_from_str("not-a-time")
        with pytest.raises(ValueError):
            param._cast_from_str("25:00:00")

    def test_parameter_url_cast_from_str(self):
        param = ParameterUrl(name="test")
        assert param._cast_from_str("https://example.com") == "https://example.com"
        assert (
            param._cast_from_str("  https://example.com  ") == "https://example.com"
        )
        assert (
            param._cast_from_str("http://localhost:8000/path")
            == "http://localhost:8000/path"
        )

    def test_parameter_url_cast_from_str_invalid(self):
        param = ParameterUrl(name="test")
        with pytest.raises(ValueError, match="Invalid URL"):
            param._cast_from_str("not-a-url")
        with pytest.raises(ValueError, match="Invalid URL"):
            param._cast_from_str("ftp://invalid")

    def test_parameter_email_cast_from_str(self):
        param = ParameterEmail(name="test")
        assert param._cast_from_str("test@example.com") == "test@example.com"
        assert param._cast_from_str("  user@domain.org  ") == "user@domain.org"

    def test_parameter_email_cast_from_str_invalid(self):
        param = ParameterEmail(name="test")
        with pytest.raises(ValueError, match="Invalid email"):
            param._cast_from_str("not-an-email")
        with pytest.raises(ValueError, match="Invalid email"):
            param._cast_from_str("missing@")

    def test_parameter_json_cast_from_str(self):
        param = ParameterJson(name="test")
        assert param._cast_from_str('{"key": "value"}') == {"key": "value"}
        assert param._cast_from_str("[1, 2, 3]") == [1, 2, 3]
        assert param._cast_from_str('{"nested": {"a": 1}}') == {"nested": {"a": 1}}
        assert param._cast_from_str("[]") == []
        assert param._cast_from_str("{}") == {}

    def test_parameter_json_cast_from_str_invalid(self):
        param = ParameterJson(name="test")
        with pytest.raises(json.JSONDecodeError):
            param._cast_from_str("not valid json")
        with pytest.raises(json.JSONDecodeError):
            param._cast_from_str("{key: value}")

    def test_parameter_list_cast_from_str(self):
        param = ParameterList(name="test")
        assert param._cast_from_str("a,b,c") == ["a", "b", "c"]
        assert param._cast_from_str("a, b, c") == ["a", "b", "c"]
        assert param._cast_from_str("single") == ["single"]
        assert param._cast_from_str("") == []
        assert param._cast_from_str("  ") == []

    def test_parameter_dict_cast_from_str(self):
        param = ParameterDict(name="test")
        assert param._cast_from_str('{"key": "value"}') == {"key": "value"}
        assert param._cast_from_str('{"a": 1, "b": 2}') == {"a": 1, "b": 2}

    def test_parameter_dict_cast_from_str_invalid(self):
        param = ParameterDict(name="test")
        with pytest.raises(ValueError, match="Expected dict"):
            param._cast_from_str("[1, 2, 3]")
        with pytest.raises(json.JSONDecodeError):
            param._cast_from_str("not json")

    def test_parameter_path_cast_from_str(self):
        param = ParameterPath(name="test")
        assert param._cast_from_str("/path/to/file") == Path("/path/to/file")
        assert param._cast_from_str("  /path/to/file  ") == Path("/path/to/file")
        assert param._cast_from_str("relative/path") == Path("relative/path")

    def test_parameter_duration_cast_from_str(self):
        param = ParameterDuration(name="test")
        assert param._cast_from_str("3600") == timedelta(seconds=3600)
        assert param._cast_from_str("3600.5") == timedelta(seconds=3600.5)
        assert param._cast_from_str("0") == timedelta(seconds=0)

    def test_parameter_duration_cast_from_str_invalid(self):
        param = ParameterDuration(name="test")
        with pytest.raises(ValueError):
            param._cast_from_str("not-a-duration")

    def test_parameter_percentage_cast_from_str(self):
        param = ParameterPercentage(name="test")
        assert param._cast_from_str("75.5") == 75.5
        assert param._cast_from_str("0") == 0.0
        assert param._cast_from_str("100") == 100.0

    def test_parameter_percentage_cast_from_str_out_of_range(self):
        param = ParameterPercentage(name="test")
        with pytest.raises(ValueError, match="must be between 0 and 100"):
            param._cast_from_str("150")
        with pytest.raises(ValueError, match="must be between 0 and 100"):
            param._cast_from_str("-10")


class TestParameterCastToStr:
    """Tests for _cast_to_str method on all parameter types."""

    def test_parameter_str_cast_to_str(self):
        param = ParameterStr(name="test")
        assert param._cast_to_str("hello") == "hello"
        assert param._cast_to_str("  spaced  ") == "spaced"  # stripped
        assert param._cast_to_str("") == ""

    def test_parameter_int_cast_to_str(self):
        param = ParameterInt(name="test")
        assert param._cast_to_str(42) == "42"
        assert param._cast_to_str(-10) == "-10"
        assert param._cast_to_str(0) == "0"

    def test_parameter_float_cast_to_str(self):
        # ParameterFloat uses base class _cast_to_str which calls str()
        param = ParameterFloat(name="test")
        assert param._cast_to_str(3.14) == "3.14"
        assert param._cast_to_str(-2.5) == "-2.5"
        assert param._cast_to_str(0.0) == "0.0"

    def test_parameter_decimal_cast_to_str(self):
        # ParameterDecimal uses base class _cast_to_str which calls str()
        param = ParameterDecimal(name="test")
        assert param._cast_to_str(Decimal("3.14159")) == "3.14159"
        assert param._cast_to_str(Decimal("-100.50")) == "-100.50"

    def test_parameter_bool_cast_to_str(self):
        param = ParameterBool(name="test")
        assert param._cast_to_str(True) == "1"
        assert param._cast_to_str(False) == "0"

    def test_parameter_date_cast_to_str(self):
        param = ParameterDate(name="test")
        assert param._cast_to_str(date(2024, 3, 15)) == "2024-03-15"
        assert param._cast_to_str(date(2000, 1, 1)) == "2000-01-01"

    def test_parameter_datetime_cast_to_str(self):
        param = ParameterDatetime(name="test")
        assert (
            param._cast_to_str(datetime(2024, 3, 15, 14, 30, 0))
            == "2024-03-15T14:30:00"
        )
        assert (
            param._cast_to_str(datetime(2024, 3, 15, 14, 30, 0, 123456))
            == "2024-03-15T14:30:00.123456"
        )

    def test_parameter_time_cast_to_str(self):
        param = ParameterTime(name="test")
        assert param._cast_to_str(time(14, 30, 0)) == "14:30:00"
        assert param._cast_to_str(time(0, 0, 0)) == "00:00:00"
        assert param._cast_to_str(time(23, 59, 59)) == "23:59:59"

    def test_parameter_url_cast_to_str(self):
        # ParameterUrl uses base class _cast_to_str
        param = ParameterUrl(name="test")
        assert param._cast_to_str("https://example.com") == "https://example.com"

    def test_parameter_email_cast_to_str(self):
        # ParameterEmail uses base class _cast_to_str
        param = ParameterEmail(name="test")
        assert param._cast_to_str("test@example.com") == "test@example.com"

    def test_parameter_json_cast_to_str(self):
        param = ParameterJson(name="test")
        assert param._cast_to_str({"key": "value"}) == '{"key": "value"}'
        assert param._cast_to_str([1, 2, 3]) == "[1, 2, 3]"
        assert param._cast_to_str({}) == "{}"
        assert param._cast_to_str([]) == "[]"

    def test_parameter_list_cast_to_str(self):
        param = ParameterList(name="test")
        assert param._cast_to_str(["a", "b", "c"]) == "a,b,c"
        assert param._cast_to_str(["single"]) == "single"
        assert param._cast_to_str([]) == ""
        assert param._cast_to_str([1, 2, 3]) == "1,2,3"

    def test_parameter_dict_cast_to_str(self):
        param = ParameterDict(name="test")
        assert param._cast_to_str({"key": "value"}) == '{"key": "value"}'
        assert param._cast_to_str({}) == "{}"

    def test_parameter_path_cast_to_str(self):
        # ParameterPath uses base class _cast_to_str
        param = ParameterPath(name="test")
        assert param._cast_to_str(Path("/path/to/file")) == "/path/to/file"

    def test_parameter_duration_cast_to_str(self):
        param = ParameterDuration(name="test")
        assert param._cast_to_str(timedelta(seconds=3600)) == "3600.0"
        assert param._cast_to_str(timedelta(seconds=3600.5)) == "3600.5"
        assert param._cast_to_str(timedelta(hours=1, minutes=30)) == "5400.0"

    def test_parameter_percentage_cast_to_str(self):
        # ParameterPercentage uses base class _cast_to_str
        param = ParameterPercentage(name="test")
        assert param._cast_to_str(75.5) == "75.5"
        assert param._cast_to_str(0) == "0"
        assert param._cast_to_str(100) == "100"


class TestParameterIsInstance:
    """Tests for _is_instance method on all parameter types."""

    def test_parameter_str_is_instance(self):
        param = ParameterStr(name="test")
        assert param._is_instance("hello") is True
        assert param._is_instance("") is True
        assert param._is_instance(123) is False
        assert param._is_instance(None) is False
        assert param._is_instance(["list"]) is False

    def test_parameter_int_is_instance(self):
        param = ParameterInt(name="test")
        assert param._is_instance(42) is True
        assert param._is_instance(-10) is True
        assert param._is_instance(0) is True
        assert param._is_instance("42") is False
        assert param._is_instance(3.14) is False
        assert param._is_instance(None) is False
        # Note: bool is subclass of int in Python
        assert param._is_instance(True) is True

    def test_parameter_float_is_instance(self):
        param = ParameterFloat(name="test")
        assert param._is_instance(3.14) is True
        assert param._is_instance(0.0) is True
        assert param._is_instance(-2.5) is True
        assert param._is_instance("3.14") is False
        assert param._is_instance(42) is False  # int is not float
        assert param._is_instance(None) is False

    def test_parameter_decimal_is_instance(self):
        param = ParameterDecimal(name="test")
        assert param._is_instance(Decimal("3.14")) is True
        assert param._is_instance(Decimal("0")) is True
        assert param._is_instance(3.14) is False
        assert param._is_instance("3.14") is False
        assert param._is_instance(42) is False

    def test_parameter_bool_is_instance(self):
        param = ParameterBool(name="test")
        assert param._is_instance(True) is True
        assert param._is_instance(False) is True
        assert param._is_instance(1) is False  # int is not bool for this check
        assert param._is_instance(0) is False
        assert param._is_instance("true") is False
        assert param._is_instance(None) is False

    def test_parameter_date_is_instance(self):
        param = ParameterDate(name="test")
        assert param._is_instance(date(2024, 3, 15)) is True
        # datetime is NOT accepted (should use ParameterDatetime)
        assert param._is_instance(datetime(2024, 3, 15, 14, 30)) is False
        assert param._is_instance("2024-03-15") is False
        assert param._is_instance(None) is False

    def test_parameter_datetime_is_instance(self):
        param = ParameterDatetime(name="test")
        assert param._is_instance(datetime(2024, 3, 15, 14, 30)) is True
        assert param._is_instance(datetime(2024, 3, 15)) is True
        # date alone is also datetime subclass behavior, but datetime check passes
        assert param._is_instance(date(2024, 3, 15)) is False
        assert param._is_instance("2024-03-15T14:30:00") is False
        assert param._is_instance(None) is False

    def test_parameter_time_is_instance(self):
        param = ParameterTime(name="test")
        assert param._is_instance(time(14, 30)) is True
        assert param._is_instance(time(0, 0, 0)) is True
        assert param._is_instance("14:30:00") is False
        assert param._is_instance(datetime(2024, 3, 15, 14, 30)) is False
        assert param._is_instance(None) is False

    def test_parameter_url_is_instance(self):
        param = ParameterUrl(name="test")
        assert param._is_instance("https://example.com") is True
        assert param._is_instance("http://localhost:8000") is True
        assert param._is_instance("not-a-url") is False
        assert param._is_instance("ftp://invalid") is False
        assert param._is_instance(123) is False
        assert param._is_instance(None) is False

    def test_parameter_email_is_instance(self):
        param = ParameterEmail(name="test")
        assert param._is_instance("test@example.com") is True
        assert param._is_instance("user@domain.org") is True
        assert param._is_instance("not-an-email") is False
        assert param._is_instance("missing@") is False
        assert param._is_instance(123) is False
        assert param._is_instance(None) is False

    def test_parameter_json_is_instance(self):
        param = ParameterJson(name="test")
        assert param._is_instance({"key": "value"}) is True
        assert param._is_instance([1, 2, 3]) is True
        assert param._is_instance({}) is True
        assert param._is_instance([]) is True
        assert param._is_instance("string") is False
        assert param._is_instance(123) is False
        assert param._is_instance(None) is False
        # Non-serializable should return False
        assert param._is_instance({"func": lambda x: x}) is False

    def test_parameter_list_is_instance(self):
        param = ParameterList(name="test")
        assert param._is_instance(["a", "b", "c"]) is True
        assert param._is_instance([]) is True
        assert param._is_instance([1, 2, 3]) is True
        assert param._is_instance("a,b,c") is False
        assert param._is_instance({"key": "value"}) is False
        assert param._is_instance(None) is False
        assert param._is_instance((1, 2, 3)) is False  # tuple is not list

    def test_parameter_dict_is_instance(self):
        param = ParameterDict(name="test")
        assert param._is_instance({"key": "value"}) is True
        assert param._is_instance({}) is True
        assert param._is_instance({"a": 1, "b": 2}) is True
        assert param._is_instance([1, 2, 3]) is False
        assert param._is_instance("string") is False
        assert param._is_instance(None) is False

    def test_parameter_path_is_instance(self):
        param = ParameterPath(name="test")
        assert param._is_instance(Path("/path/to/file")) is True
        assert param._is_instance(Path(".")) is True
        assert param._is_instance("/path/to/file") is False
        assert param._is_instance(None) is False

    def test_parameter_duration_is_instance(self):
        param = ParameterDuration(name="test")
        assert param._is_instance(timedelta(seconds=3600)) is True
        assert param._is_instance(timedelta(hours=1)) is True
        assert param._is_instance(timedelta()) is True
        assert param._is_instance(3600) is False
        assert param._is_instance("3600") is False
        assert param._is_instance(None) is False

    def test_parameter_percentage_is_instance(self):
        param = ParameterPercentage(name="test")
        assert param._is_instance(75.5) is True
        assert param._is_instance(0.0) is True
        assert param._is_instance(100) is True  # int is also accepted
        assert param._is_instance(50) is True
        assert param._is_instance("75.5") is False
        assert param._is_instance(None) is False


class TestParameterCastRoundtrip:
    """Test that _cast_from_str and _cast_to_str are inverse operations."""

    @pytest.mark.parametrize(
        "param_class,original_value",
        [
            (ParameterStr, "hello world"),
            (ParameterInt, 42),
            (ParameterFloat, 3.14),
            (ParameterDecimal, Decimal("3.14159")),
            (ParameterBool, True),
            (ParameterBool, False),
            (ParameterDate, date(2024, 3, 15)),
            (ParameterDatetime, datetime(2024, 3, 15, 14, 30, 0)),
            (ParameterTime, time(14, 30, 0)),
            (ParameterUrl, "https://example.com"),
            (ParameterEmail, "test@example.com"),
            (ParameterJson, {"key": "value", "number": 42}),
            (ParameterJson, [1, 2, 3]),
            (ParameterList, ["a", "b", "c"]),
            (ParameterDict, {"key": "value"}),
            (ParameterPath, Path("/path/to/file")),
            (ParameterDuration, timedelta(seconds=3600)),
            (ParameterPercentage, 75.5),
        ],
    )
    def test_roundtrip(
        self, param_class: type[Parameter], original_value: Any
    ) -> None:
        """Test that value -> str -> value produces the original value."""
        param = param_class(name="test")
        str_value = param._cast_to_str(original_value)
        restored_value = param._cast_from_str(str_value)
        assert restored_value == original_value
