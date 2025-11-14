"""Tests for admin views using Django test client"""

import json

import pytest
from django.contrib.admin.sites import AdminSite
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
def regular_user(db):
    """Create a regular user (non-staff) for testing"""
    return User.objects.create_user(
        username="user", email="user@test.com", password="user123"
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
class TestParameterAdminListView:
    """Tests for Parameter admin changelist view"""

    def test_admin_list_view_requires_login(self):
        """Test that changelist requires authentication"""
        client = Client()
        url = reverse("admin:django_app_parameter_parameter_changelist")
        response = client.get(url)

        # Should redirect to login
        assert response.status_code == 302
        assert "/admin/login/" in response.url

    def test_admin_list_view_requires_staff(self, regular_user):
        """Test that changelist requires staff permission"""
        client = Client()
        client.login(username="user", password="user123")
        url = reverse("admin:django_app_parameter_parameter_changelist")
        response = client.get(url)

        # Non-staff users should be redirected to login
        assert response.status_code == 302

    def test_admin_list_view_accessible_by_admin(self, admin_client):
        """Test that admin can access changelist"""
        url = reverse("admin:django_app_parameter_parameter_changelist")
        response = admin_client.get(url)

        assert response.status_code == 200
        assert "django_app_parameter/parameter" in str(response.context)

    def test_admin_list_view_displays_parameters(
        self, admin_client, sample_parameter
    ):
        """Test that changelist displays existing parameters"""
        url = reverse("admin:django_app_parameter_parameter_changelist")
        response = admin_client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert "TEST_PARAMETER" in content
        assert "Test Parameter" in content

    def test_admin_list_view_empty(self, admin_client):
        """Test changelist when no parameters exist"""
        url = reverse("admin:django_app_parameter_parameter_changelist")
        response = admin_client.get(url)

        assert response.status_code == 200
        # Should show "0 parameters" or similar
        content = response.content.decode()
        assert "0 parameters" in content or "No parameters" in content.lower()


@pytest.mark.django_db
class TestParameterAdminAddView:
    """Tests for Parameter admin add view"""

    def test_admin_add_view_requires_login(self):
        """Test that add view requires authentication"""
        client = Client()
        url = reverse("admin:django_app_parameter_parameter_add")
        response = client.get(url)

        assert response.status_code == 302
        assert "/admin/login/" in response.url

    def test_admin_add_view_accessible_by_admin(self, admin_client):
        """Test that admin can access add view"""
        url = reverse("admin:django_app_parameter_parameter_add")
        response = admin_client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert "name" in content.lower()
        assert "slug" in content.lower()
        assert "value_type" in content.lower()

    def test_admin_add_view_create_parameter(self, admin_client):
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

        # Should redirect to changelist after success
        assert response.status_code == 200
        assert Parameter.objects.filter(slug="NEW_PARAMETER").exists()

        param = Parameter.objects.get(slug="NEW_PARAMETER")
        assert param.name == "New Parameter"
        assert param.value_type == "STR"
        assert param.is_global is True

    def test_admin_add_view_auto_generate_slug(self, admin_client):
        """Test that slug is auto-generated if not provided"""
        url = reverse("admin:django_app_parameter_parameter_add")
        data = {
            "name": "My Test Param",
            "slug": "",  # Empty slug
            "value_type": "INT",
            "description": "",
            "is_global": "",
        }
        response = admin_client.post(url, data, follow=True)

        assert response.status_code == 200
        # Slug should be auto-generated from name
        assert Parameter.objects.filter(slug="MY_TEST_PARAM").exists()

    def test_admin_add_view_validation_error(self, admin_client):
        """Test that form validation errors are displayed"""
        url = reverse("admin:django_app_parameter_parameter_add")
        data = {
            "name": "",  # Missing required field
            "slug": "TEST",
            "value_type": "STR",
        }
        response = admin_client.post(url, data)

        assert response.status_code == 200
        # Should show form with errors
        content = response.content.decode()
        assert "error" in content.lower() or "required" in content.lower()


@pytest.mark.django_db
class TestParameterAdminChangeView:
    """Tests for Parameter admin change view"""

    def test_admin_change_view_requires_login(self, sample_parameter):
        """Test that change view requires authentication"""
        client = Client()
        url = reverse(
            "admin:django_app_parameter_parameter_change",
            args=[sample_parameter.pk],
        )
        response = client.get(url)

        assert response.status_code == 302
        assert "/admin/login/" in response.url

    def test_admin_change_view_accessible_by_admin(
        self, admin_client, sample_parameter
    ):
        """Test that admin can access change view"""
        url = reverse(
            "admin:django_app_parameter_parameter_change",
            args=[sample_parameter.pk],
        )
        response = admin_client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert "Test Parameter" in content
        assert "test value" in content

    def test_admin_change_view_readonly_fields(
        self, admin_client, sample_parameter
    ):
        """Test that slug and value_type are readonly in change view"""
        url = reverse(
            "admin:django_app_parameter_parameter_change",
            args=[sample_parameter.pk],
        )
        response = admin_client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        # Readonly fields should be displayed but not editable
        assert "TEST_PARAMETER" in content
        # The value_type is displayed as its label, not the code
        assert ("Chaîne de caractères" in content or "STR" in content or "String" in content)

    def test_admin_change_view_update_value(self, admin_client, sample_parameter):
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
            # Include validator formset data (empty but required)
            "validators-TOTAL_FORMS": "0",
            "validators-INITIAL_FORMS": "0",
            "validators-MIN_NUM_FORMS": "0",
            "validators-MAX_NUM_FORMS": "1000",
        }
        response = admin_client.post(url, data, follow=True)

        assert response.status_code == 200
        sample_parameter.refresh_from_db()
        assert sample_parameter.value == "updated value"
        assert sample_parameter.description == "Updated description"

    def test_admin_change_view_nonexistent_parameter(self, admin_client):
        """Test accessing change view with invalid parameter ID"""
        url = reverse(
            "admin:django_app_parameter_parameter_change", args=[99999]
        )
        response = admin_client.get(url)

        # Should return 404 or redirect
        assert response.status_code in [302, 404]


@pytest.mark.django_db
class TestParameterAdminDeleteView:
    """Tests for Parameter admin delete view"""

    def test_admin_delete_view_requires_login(self, sample_parameter):
        """Test that delete view requires authentication"""
        client = Client()
        url = reverse(
            "admin:django_app_parameter_parameter_delete",
            args=[sample_parameter.pk],
        )
        response = client.get(url)

        assert response.status_code == 302
        assert "/admin/login/" in response.url

    def test_admin_delete_view_accessible_by_admin(
        self, admin_client, sample_parameter
    ):
        """Test that admin can access delete confirmation page"""
        url = reverse(
            "admin:django_app_parameter_parameter_delete",
            args=[sample_parameter.pk],
        )
        response = admin_client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        assert "Are you sure" in content or "confirm" in content.lower()
        assert "Test Parameter" in content

    def test_admin_delete_view_delete_parameter(
        self, admin_client, sample_parameter
    ):
        """Test deleting a parameter through admin"""
        param_id = sample_parameter.pk
        url = reverse(
            "admin:django_app_parameter_parameter_delete", args=[param_id]
        )
        data = {"post": "yes"}  # Confirm deletion
        response = admin_client.post(url, data, follow=True)

        assert response.status_code == 200
        # Parameter should be deleted
        assert not Parameter.objects.filter(pk=param_id).exists()


@pytest.mark.django_db
class TestParameterAdminWithValidators:
    """Tests for Parameter admin with validators inline"""

    def test_admin_change_view_shows_validators_inline(self, admin_client):
        """Test that validators inline is shown when editing parameter"""
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

        url = reverse(
            "admin:django_app_parameter_parameter_change", args=[param.pk]
        )
        response = admin_client.get(url)

        assert response.status_code == 200
        content = response.content.decode()
        # Should show inline formset for validators
        assert "MinValueValidator" in content or "validator" in content.lower()

    def test_admin_create_parameter_with_validator(self, admin_client):
        """Test creating parameter and adding validator inline"""
        # First create the parameter
        param = Parameter.objects.create(
            name="Validated Param",
            slug="VALIDATED_PARAM",
            value="100",
            value_type="INT",
        )

        # Now edit it to add a validator
        url = reverse(
            "admin:django_app_parameter_parameter_change", args=[param.pk]
        )

        # Simulate adding a validator through inline
        data = {
            "name": "Validated Param",
            "value": "100",
            "description": "",
            "is_global": "",
            # Inline formset data
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
        # Validator should be created
        assert ParameterValidator.objects.filter(parameter=param).count() == 1

        validator = ParameterValidator.objects.get(parameter=param)
        assert validator.validator_type == "MinValueValidator"
        assert validator.validator_params == {"limit_value": 50}


@pytest.mark.django_db
class TestParameterAdminIntegerType:
    """Tests for admin with INTEGER type parameters"""

    def test_admin_create_integer_parameter(self, admin_client):
        """Test creating an integer parameter through admin"""
        url = reverse("admin:django_app_parameter_parameter_add")
        data = {
            "name": "Integer Param",
            "slug": "INTEGER_PARAM",
            "value_type": "INT",
            "description": "An integer parameter",
            "is_global": "",
        }
        response = admin_client.post(url, data, follow=True)

        assert response.status_code == 200
        param = Parameter.objects.get(slug="INTEGER_PARAM")
        assert param.value_type == "INT"
        # Default value for INT should be "0"
        assert param.value == "0"

    def test_admin_update_integer_value(self, admin_client):
        """Test updating integer value through admin"""
        param = Parameter.objects.create(
            name="Count", slug="COUNT", value="0", value_type="INT"
        )

        url = reverse(
            "admin:django_app_parameter_parameter_change", args=[param.pk]
        )
        data = {
            "name": "Count",
            "value": "42",
            "description": "",
            "is_global": "",
            # Include validator formset data (empty but required)
            "validators-TOTAL_FORMS": "0",
            "validators-INITIAL_FORMS": "0",
            "validators-MIN_NUM_FORMS": "0",
            "validators-MAX_NUM_FORMS": "1000",
        }
        response = admin_client.post(url, data, follow=True)

        assert response.status_code == 200
        param.refresh_from_db()
        assert param.value == "42"

    def test_admin_integer_validation_error(self, admin_client):
        """Test that invalid integer value shows error"""
        param = Parameter.objects.create(
            name="Count", slug="COUNT", value="0", value_type="INT"
        )

        url = reverse(
            "admin:django_app_parameter_parameter_change", args=[param.pk]
        )
        data = {
            "name": "Count",
            "value": "not_a_number",
            "description": "",
            "is_global": "",
        }
        response = admin_client.post(url, data)

        # Should show validation error
        assert response.status_code == 200
        content = response.content.decode()
        assert "error" in content.lower() or "invalid" in content.lower()


@pytest.mark.django_db
class TestParameterAdminBooleanType:
    """Tests for admin with BOOLEAN type parameters"""

    def test_admin_create_boolean_parameter(self, admin_client):
        """Test creating a boolean parameter through admin"""
        url = reverse("admin:django_app_parameter_parameter_add")
        data = {
            "name": "Feature Flag",
            "slug": "FEATURE_FLAG",
            "value_type": "BOO",
            "description": "Enable/disable feature",
            "is_global": "",
        }
        response = admin_client.post(url, data, follow=True)

        assert response.status_code == 200
        param = Parameter.objects.get(slug="FEATURE_FLAG")
        assert param.value_type == "BOO"
        # Default value for BOO should be "0" (False)
        assert param.value == "0"

    def test_admin_update_boolean_value(self, admin_client):
        """Test updating boolean value through admin"""
        param = Parameter.objects.create(
            name="Enabled", slug="ENABLED", value="0", value_type="BOO"
        )

        url = reverse(
            "admin:django_app_parameter_parameter_change", args=[param.pk]
        )
        data = {
            "name": "Enabled",
            "value": "on",  # Checkbox checked
            "description": "",
            "is_global": "",
            # Include validator formset data (empty but required)
            "validators-TOTAL_FORMS": "0",
            "validators-INITIAL_FORMS": "0",
            "validators-MIN_NUM_FORMS": "0",
            "validators-MAX_NUM_FORMS": "1000",
        }
        response = admin_client.post(url, data, follow=True)

        assert response.status_code == 200
        param.refresh_from_db()
        assert param.value == "1"  # True


@pytest.mark.django_db
class TestParameterAdminSearch:
    """Tests for admin search functionality"""

    def test_admin_search_by_name(self, admin_client):
        """Test searching parameters by name"""
        Parameter.objects.create(
            name="Email Address", slug="EMAIL_ADDRESS", value="test@test.com"
        )
        Parameter.objects.create(
            name="Phone Number", slug="PHONE_NUMBER", value="123456"
        )

        url = reverse("admin:django_app_parameter_parameter_changelist")
        response = admin_client.get(url, {"q": "Email"})

        assert response.status_code == 200
        content = response.content.decode()
        assert "EMAIL_ADDRESS" in content
        assert "PHONE_NUMBER" not in content

    def test_admin_search_by_slug(self, admin_client):
        """Test searching parameters by slug"""
        Parameter.objects.create(
            name="Email Address", slug="EMAIL_ADDRESS", value="test@test.com"
        )
        Parameter.objects.create(
            name="Phone Number", slug="PHONE_NUMBER", value="123456"
        )

        url = reverse("admin:django_app_parameter_parameter_changelist")
        response = admin_client.get(url, {"q": "PHONE"})

        assert response.status_code == 200
        content = response.content.decode()
        assert "PHONE_NUMBER" in content
        assert "EMAIL_ADDRESS" not in content


@pytest.mark.django_db
class TestParameterAdminFilters:
    """Tests for admin list filters"""

    def test_admin_filter_by_value_type(self, admin_client):
        """Test filtering parameters by value type"""
        Parameter.objects.create(
            name="String Param", slug="STRING_PARAM", value="text", value_type="STR"
        )
        Parameter.objects.create(
            name="Int Param", slug="INT_PARAM", value="42", value_type="INT"
        )

        url = reverse("admin:django_app_parameter_parameter_changelist")
        response = admin_client.get(url, {"value_type": "INT"})

        assert response.status_code == 200
        content = response.content.decode()
        assert "INT_PARAM" in content

    def test_admin_filter_by_is_global(self, admin_client):
        """Test filtering parameters by is_global flag"""
        Parameter.objects.create(
            name="Global Param",
            slug="GLOBAL_PARAM",
            value="test",
            is_global=True,
        )
        Parameter.objects.create(
            name="Local Param",
            slug="LOCAL_PARAM",
            value="test",
            is_global=False,
        )

        url = reverse("admin:django_app_parameter_parameter_changelist")
        response = admin_client.get(url, {"is_global__exact": "1"})

        assert response.status_code == 200
        content = response.content.decode()
        assert "GLOBAL_PARAM" in content
