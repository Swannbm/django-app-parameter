"""Tests for admin views using Django test client - Critical tests only"""

import json

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from django_app_parameter.models import Parameter, ParameterValidator


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing"""
    return User.objects.create_superuser(
        username="admin", email="admin@test.com", password="admin123"
    )


@pytest.fixture
def admin_client(admin_user):
    """Create a client logged in as admin"""
    client = Client()
    client.login(username="admin", password="admin123")
    return client


@pytest.fixture
def sample_parameter(db):
    """Create a sample parameter for testing"""
    return Parameter.objects.create(
        name="Test Parameter",
        slug="TEST_PARAMETER",
        value="test value",
        value_type="STR",
        description="Test description",
        is_global=True,
    )


@pytest.mark.django_db
class TestParameterAdminSecurity:
    """Critical security tests for admin authentication"""

    def test_admin_list_view_requires_login(self):
        """Test that changelist requires authentication"""
        client = Client()
        url = reverse("admin:django_app_parameter_parameter_changelist")
        response = client.get(url)
        assert response.status_code == 302
        assert "/admin/login/" in response.url

    def test_admin_add_view_requires_login(self):
        """Test that add view requires authentication"""
        client = Client()
        url = reverse("admin:django_app_parameter_parameter_add")
        response = client.get(url)
        assert response.status_code == 302
        assert "/admin/login/" in response.url


@pytest.mark.django_db
class TestParameterAdminCRUD:
    """Critical CRUD operations tests"""

    def test_admin_create_parameter(self, admin_client):
        """Test creating a new parameter through admin"""
        url = reverse("admin:django_app_parameter_parameter_add")
        data = {
            "name": "New Parameter",
            "slug": "NEW_PARAMETER",
            "value_type": "STR",
            "description": "New description",
            "is_global": "on",
        }
        response = admin_client.post(url, data, follow=True)

        assert response.status_code == 200
        assert Parameter.objects.filter(slug="NEW_PARAMETER").exists()
        param = Parameter.objects.get(slug="NEW_PARAMETER")
        assert param.name == "New Parameter"
        assert param.value_type == "STR"

    def test_admin_update_parameter(self, admin_client, sample_parameter):
        """Test updating parameter value through admin"""
        url = reverse(
            "admin:django_app_parameter_parameter_change",
            args=[sample_parameter.pk],
        )
        data = {
            "name": "Test Parameter",
            "value": "updated value",
            "description": "Updated description",
            "is_global": "on",
            "validators-TOTAL_FORMS": "0",
            "validators-INITIAL_FORMS": "0",
            "validators-MIN_NUM_FORMS": "0",
            "validators-MAX_NUM_FORMS": "1000",
        }
        response = admin_client.post(url, data, follow=True)

        assert response.status_code == 200
        sample_parameter.refresh_from_db()
        assert sample_parameter.value == "updated value"

    def test_admin_delete_parameter(self, admin_client, sample_parameter):
        """Test deleting a parameter through admin"""
        param_id = sample_parameter.pk
        url = reverse("admin:django_app_parameter_parameter_delete", args=[param_id])
        data = {"post": "yes"}
        response = admin_client.post(url, data, follow=True)

        assert response.status_code == 200
        assert not Parameter.objects.filter(pk=param_id).exists()


@pytest.mark.django_db
class TestParameterAdminValidation:
    """Critical validation tests"""

    def test_admin_validation_error(self, admin_client):
        """Test that form validation errors are displayed"""
        url = reverse("admin:django_app_parameter_parameter_add")
        data = {
            "name": "",  # Missing required field
            "slug": "TEST",
            "value_type": "STR",
        }
        response = admin_client.post(url, data)

        assert response.status_code == 200
        content = response.content.decode()
        assert "error" in content.lower() or "required" in content.lower()

    def test_admin_integer_validation(self, admin_client):
        """Test that invalid integer value shows error"""
        param = Parameter.objects.create(
            name="Count", slug="COUNT", value="0", value_type="INT"
        )

        url = reverse("admin:django_app_parameter_parameter_change", args=[param.pk])
        data = {
            "name": "Count",
            "value": "not_a_number",
            "description": "",
            "is_global": "",
        }
        response = admin_client.post(url, data)

        assert response.status_code == 200
        content = response.content.decode()
        assert "error" in content.lower() or "invalid" in content.lower()


@pytest.mark.django_db
class TestParameterAdminValidators:
    """Critical tests for validator inline functionality"""

    def test_admin_create_parameter_with_validator(self, admin_client):
        """Test creating parameter and adding validator inline"""
        param = Parameter.objects.create(
            name="Validated Param",
            slug="VALIDATED_PARAM",
            value="100",
            value_type="INT",
        )

        url = reverse("admin:django_app_parameter_parameter_change", args=[param.pk])
        data = {
            "name": "Validated Param",
            "value": "100",
            "description": "",
            "is_global": "",
            "validators-TOTAL_FORMS": "1",
            "validators-INITIAL_FORMS": "0",
            "validators-MIN_NUM_FORMS": "0",
            "validators-MAX_NUM_FORMS": "1000",
            "validators-0-validator_type": "MinValueValidator",
            "validators-0-validator_params": json.dumps({"limit_value": 50}),
            "validators-0-parameter": str(param.pk),
        }
        response = admin_client.post(url, data, follow=True)

        assert response.status_code == 200
        assert ParameterValidator.objects.filter(parameter=param).count() == 1
        validator = ParameterValidator.objects.get(parameter=param)
        assert validator.validator_type == "MinValueValidator"
        assert validator.validator_params == {"limit_value": 50}
