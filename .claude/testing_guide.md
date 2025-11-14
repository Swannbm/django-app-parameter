# Guide de testing

## 🎯 Stratégie de tests

### Objectifs
- **100% de couverture de code** (requis)
- Tests unitaires pour toute la logique métier
- Tests d'intégration pour l'admin Django
- Tests de bout en bout pour les commandes de management
- Tests de régression pour éviter les bugs récurrents

### Stack de tests
- **pytest**: Framework de tests
- **pytest-django**: Plugin Django pour pytest
- **pytest-cov**: Couverture de code
- **SQLite en mémoire**: Base de données de tests rapide

## 📁 Organisation des tests

### Structure
```
tests/
├── settings.py              # Configuration Django pour tests
├── urls.py                  # URLs pour tests admin
├── test_django_app_parameter.py  # Tests du modèle (2,063 lignes)
├── test_admin.py                 # Tests formulaires admin (787 lignes)
├── test_admin_views.py           # Tests vues admin (562 lignes)
├── test_dump_param.py            # Tests commande export (363 lignes)
├── test_utils.py                 # Tests utilitaires (308 lignes)
└── test_validators.py            # Tests validateurs (75 lignes)
```

### Fichiers de test par composant

**[test_django_app_parameter.py](tests/test_django_app_parameter.py)** (2,063 lignes):
- Tests du modèle Parameter
- Tests des getters pour tous les types
- Tests des setters avec validation
- Tests du ParameterManager
- Tests du proxy app_parameter
- Tests du context processor

**[test_admin.py](tests/test_admin.py)** (787 lignes):
- Tests des formulaires admin (create/edit)
- Tests de personnalisation des champs
- Tests des inlines de validateurs
- Tests du routing de formulaires

**[test_admin_views.py](tests/test_admin_views.py)** (562 lignes):
- Tests d'intégration avec Django test client
- Tests des vues CRUD de l'admin
- Tests des permissions
- Tests du rendu des templates

**[test_dump_param.py](tests/test_dump_param.py)** (363 lignes):
- Tests de la commande dump_param
- Tests du format JSON
- Tests de l'export des validateurs

**[test_utils.py](tests/test_utils.py)** (308 lignes):
- Tests du registre de validateurs
- Tests d'import de validateurs personnalisés
- Tests de récupération des settings

**[test_validators.py](tests/test_validators.py)** (75 lignes):
- Tests d'instanciation des validateurs
- Tests d'exécution des validations

## 🧪 Configuration de test

### [tests/settings.py](tests/settings.py)

Configuration minimale Django pour tests:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Base en mémoire = rapide
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django_app_parameter',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_app_parameter.context_processors.add_global_parameter_context',
            ],
        },
    },
]

SECRET_KEY = 'test-secret-key'
USE_TZ = True
```

### pytest.ini

```ini
[pytest]
DJANGO_SETTINGS_MODULE = tests.settings
python_files = tests/test_*.py
addopts =
    --strict-markers
    --tb=short
    --ds=tests.settings
```

### pyproject.toml (coverage)

```toml
[tool.coverage.run]
source = ["django_app_parameter"]
omit = [
    "*/migrations/*",
    "*/tests/*",
    "*/.venv/*",
    "*/.tox/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
]
fail_under = 100
```

## 🔧 Commandes de test

### Exécution de base

```bash
# Tous les tests
poetry run pytest

# Tests spécifiques
poetry run pytest tests/test_admin.py
poetry run pytest tests/test_admin.py::TestParameterAdmin
poetry run pytest tests/test_admin.py::TestParameterAdmin::test_specific_case

# Tests avec pattern
poetry run pytest -k "validator"
poetry run pytest -k "admin and not views"

# Verbose
poetry run pytest -v
poetry run pytest -vv

# Stop au premier échec
poetry run pytest -x

# Afficher print() dans les tests
poetry run pytest -s
```

### Couverture de code

```bash
# Avec rapport dans le terminal
poetry run pytest --cov=django_app_parameter --cov-report=term

# Avec rapport HTML
poetry run pytest --cov=django_app_parameter --cov-report=html

# Les deux
poetry run pytest --cov=django_app_parameter --cov-report=term --cov-report=html

# Ouvrir le rapport HTML
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Vérifier couverture 100%
poetry run coverage run -m pytest
poetry run coverage report --fail-under=100
```

### Tests multi-versions avec Tox

```bash
# Tous les environnements (8 combinaisons)
tox

# Environnement spécifique
tox -e py310-django42
tox -e py313-django52

# Parallélisation
tox -p auto

# Recréer l'environnement
tox -r -e py310-django42
```

## 📝 Écrire des tests

### Pattern de base

```python
import pytest
from django_app_parameter.models import Parameter

def test_create_parameter(db):
    """Test création simple d'un paramètre"""
    param = Parameter.objects.create(
        name="Test Param",
        value_type=Parameter.TYPES.STR,
        value="test value"
    )
    assert param.slug == "TEST_PARAM"
    assert param.str() == "test value"
```

### Utiliser des fixtures

```python
@pytest.fixture
def string_parameter(db):
    """Fixture réutilisable"""
    return Parameter.objects.create(
        name="Test String",
        value_type=Parameter.TYPES.STR,
        value="test value"
    )

def test_with_fixture(string_parameter):
    """Test utilisant la fixture"""
    assert string_parameter.str() == "test value"
```

### Tests paramétrés

```python
@pytest.mark.parametrize("value_type,value,expected", [
    (Parameter.TYPES.INT, "42", 42),
    (Parameter.TYPES.FLT, "3.14", 3.14),
    (Parameter.TYPES.BOO, "true", True),
])
def test_parameter_conversion(db, value_type, value, expected):
    """Un test pour plusieurs cas"""
    param = Parameter.objects.create(
        name="Test",
        value_type=value_type,
        value=value
    )
    assert param.get() == expected
```

### Tests d'exceptions

```python
import pytest
from django.core.exceptions import ImproperlyConfigured, ValidationError

def test_parameter_not_found(db):
    """Test qu'une exception est levée"""
    with pytest.raises(ImproperlyConfigured) as exc_info:
        Parameter.objects.get_from_slug("NONEXISTENT")

    assert "NONEXISTENT" in str(exc_info.value)

def test_invalid_value(db):
    """Test validation"""
    param = Parameter.objects.create(
        name="Age",
        value_type=Parameter.TYPES.INT,
        value="100"
    )
    param.parametervalidator_set.create(
        validator_type="max_value",
        validator_params={"limit_value": 50}
    )

    with pytest.raises(ValidationError):
        param.set_int(99)
```

### Tests avec Django test client

```python
import pytest
from django.contrib.auth.models import User

@pytest.fixture
def admin_client(db, client):
    """Client authentifié"""
    user = User.objects.create_superuser(
        username="admin",
        email="admin@test.com",
        password="admin"
    )
    client.force_login(user)
    return client

def test_admin_add_view(admin_client):
    """Test vue d'ajout admin"""
    response = admin_client.get("/admin/django_app_parameter/parameter/add/")
    assert response.status_code == 200
    assert "Add parameter" in response.content.decode()

def test_admin_create_parameter(admin_client):
    """Test création via formulaire admin"""
    data = {
        "name": "New Param",
        "value": "test",
        "value_type": Parameter.TYPES.STR,
        "description": "Test description",
        "is_global": False,
    }
    response = admin_client.post(
        "/admin/django_app_parameter/parameter/add/",
        data
    )
    assert response.status_code == 302  # Redirect après succès

    param = Parameter.objects.get(slug="NEW_PARAM")
    assert param.value == "test"
```

### Tests de commandes de management

```python
import pytest
from io import StringIO
from django.core.management import call_command

def test_dump_param_command(db, tmp_path):
    """Test commande dump_param"""
    # Créer des paramètres
    Parameter.objects.create(
        name="Test",
        value_type=Parameter.TYPES.STR,
        value="test"
    )

    # Exécuter la commande
    output_file = tmp_path / "output.json"
    call_command("dump_param", str(output_file))

    # Vérifier le résultat
    assert output_file.exists()
    import json
    data = json.loads(output_file.read_text())
    assert len(data) == 1
    assert data[0]["slug"] == "TEST"

def test_load_param_command(db, tmp_path):
    """Test commande load_param"""
    # Créer fichier JSON
    import json
    data = [
        {
            "name": "Test Param",
            "value": "test value",
            "value_type": "STR"
        }
    ]
    json_file = tmp_path / "params.json"
    json_file.write_text(json.dumps(data))

    # Exécuter la commande
    call_command("load_param", "--file", str(json_file))

    # Vérifier le résultat
    param = Parameter.objects.get(slug="TEST_PARAM")
    assert param.value == "test value"
```

## 🎯 Exemples de tests par catégorie

### Tests de modèle

**Localisation**: [tests/test_django_app_parameter.py](tests/test_django_app_parameter.py)

```python
class TestParameterModel:
    """Tests du modèle Parameter"""

    def test_slug_generation(self, db):
        """Test génération automatique du slug"""
        param = Parameter.objects.create(
            name="My Parameter Name",
            value_type=Parameter.TYPES.STR,
            value="value"
        )
        assert param.slug == "MY_PARAMETER_NAME"

    def test_str_method(self, db):
        """Test méthode __str__"""
        param = Parameter.objects.create(
            name="Test",
            value_type=Parameter.TYPES.STR,
            value="value"
        )
        assert str(param) == "Test (TEST)"

    def test_type_conversion_int(self, db):
        """Test conversion vers int"""
        param = Parameter.objects.create(
            name="Age",
            value_type=Parameter.TYPES.INT,
            value="42"
        )
        assert param.int() == 42
        assert isinstance(param.int(), int)

    def test_set_with_validation(self, db):
        """Test setter avec validation"""
        param = Parameter.objects.create(
            name="Score",
            value_type=Parameter.TYPES.INT,
            value="50"
        )
        param.parametervalidator_set.create(
            validator_type="min_value",
            validator_params={"limit_value": 0}
        )
        param.parametervalidator_set.create(
            validator_type="max_value",
            validator_params={"limit_value": 100}
        )

        # Valeur valide
        param.set_int(75)
        assert param.int() == 75

        # Valeur invalide
        with pytest.raises(ValidationError):
            param.set_int(150)
```

### Tests de Manager

```python
class TestParameterManager:
    """Tests du ParameterManager"""

    def test_get_from_slug_success(self, db):
        """Test récupération par slug"""
        Parameter.objects.create(
            name="Test",
            value_type=Parameter.TYPES.STR,
            value="value"
        )
        param = Parameter.objects.get_from_slug("TEST")
        assert param.value == "value"

    def test_get_from_slug_not_found(self, db):
        """Test slug inexistant"""
        with pytest.raises(ImproperlyConfigured) as exc_info:
            Parameter.objects.get_from_slug("NONEXISTENT")
        assert "NONEXISTENT" in str(exc_info.value)

    def test_typed_getter_shortcut(self, db):
        """Test raccourcis typés du manager"""
        Parameter.objects.create(
            name="Age",
            value_type=Parameter.TYPES.INT,
            value="42"
        )
        age = Parameter.objects.int("AGE")
        assert age == 42
        assert isinstance(age, int)
```

### Tests de proxy

```python
from django_app_parameter import app_parameter

class TestAccessParameter:
    """Tests du proxy app_parameter"""

    def test_access_via_proxy(self, db):
        """Test accès via proxy"""
        Parameter.objects.create(
            name="Title",
            value_type=Parameter.TYPES.STR,
            value="My Title"
        )
        title = app_parameter.TITLE
        assert title == "My Title"

    def test_proxy_auto_conversion(self, db):
        """Test conversion automatique via proxy"""
        Parameter.objects.create(
            name="Count",
            value_type=Parameter.TYPES.INT,
            value="42"
        )
        count = app_parameter.COUNT
        assert count == 42
        assert isinstance(count, int)
```

### Tests d'admin

**Localisation**: [tests/test_admin.py](tests/test_admin.py)

```python
from django_app_parameter.admin import ParameterAdmin, ParameterCreateForm, ParameterEditForm

class TestParameterAdmin:
    """Tests de l'admin Parameter"""

    def test_get_form_for_create(self, rf):
        """Test formulaire pour création"""
        admin = ParameterAdmin(Parameter, admin_site)
        request = rf.get("/admin/")

        Form = admin.get_form(request, obj=None)
        assert Form == ParameterCreateForm

    def test_get_form_for_edit(self, rf, string_parameter):
        """Test formulaire pour édition"""
        admin = ParameterAdmin(Parameter, admin_site)
        request = rf.get("/admin/")

        Form = admin.get_form(request, obj=string_parameter)
        assert Form == ParameterEditForm

    def test_edit_form_boolean_field(self, db):
        """Test champ booléen dans formulaire d'édition"""
        param = Parameter.objects.create(
            name="Enabled",
            value_type=Parameter.TYPES.BOO,
            value="true"
        )
        form = ParameterEditForm(instance=param)

        # Le champ value doit être un BooleanField
        assert isinstance(form.fields['value'], forms.BooleanField)
        assert form.fields['value'].initial is True
```

### Tests de validateurs

**Localisation**: [tests/test_validators.py](tests/test_validators.py)

```python
class TestValidators:
    """Tests du système de validateurs"""

    def test_validator_instantiation(self, db):
        """Test instanciation d'un validateur"""
        param = Parameter.objects.create(
            name="Age",
            value_type=Parameter.TYPES.INT,
            value="25"
        )
        validator_obj = param.parametervalidator_set.create(
            validator_type="min_value",
            validator_params={"limit_value": 18}
        )

        validator = validator_obj.get_validator()
        # Ne doit pas lever d'exception
        validator(25)

        # Doit lever une exception
        with pytest.raises(ValidationError):
            validator(10)

    def test_custom_validator(self, db, settings):
        """Test validateur personnalisé"""
        settings.DJANGO_APP_PARAMETER = {
            'validators': {
                'even_number': 'tests.test_validators.validate_even'
            }
        }

        param = Parameter.objects.create(
            name="Even Number",
            value_type=Parameter.TYPES.INT,
            value="10"
        )
        param.parametervalidator_set.create(
            validator_type="even_number",
            validator_params={}
        )

        # Valeur paire OK
        param.set_int(20)

        # Valeur impaire erreur
        with pytest.raises(ValidationError):
            param.set_int(15)
```

## 🐛 Debugging de tests

### Utiliser pdb

```python
def test_with_pdb(db):
    """Test avec point d'arrêt"""
    param = Parameter.objects.create(
        name="Test",
        value_type=Parameter.TYPES.STR,
        value="test"
    )

    import pdb; pdb.set_trace()  # Point d'arrêt

    assert param.str() == "test"

# Exécuter avec -s pour voir pdb
# poetry run pytest tests/test_admin.py::test_with_pdb -s
```

### Afficher les print()

```bash
# Voir les print() dans les tests
poetry run pytest -s

# Avec capture désactivée et verbose
poetry run pytest -s -v
```

### Tests lents

```bash
# Afficher les 10 tests les plus lents
poetry run pytest --durations=10

# Seulement tests > 1s
poetry run pytest --durations=0 --durations-min=1.0
```

### Tests qui échouent

```bash
# Réexécuter seulement les tests qui ont échoué
poetry run pytest --lf

# Réexécuter les échecs d'abord, puis le reste
poetry run pytest --ff
```

## 📊 Métriques de qualité

### Couverture actuelle
- **Lignes de tests**: 4,158
- **Couverture**: 100%
- **Nombre de tests**: ~200+

### Objectifs
- Maintenir 100% de couverture
- Temps d'exécution < 10 secondes
- 0 avertissements pytest
- Tous les tests passent sur toutes les versions (Python 3.10-3.13, Django 4.2/5.2)

## 💡 Bonnes pratiques

1. **Un test = une chose**: Chaque test doit vérifier un seul comportement
2. **Noms explicites**: `test_parameter_validation_fails_with_negative_value`
3. **AAA Pattern**: Arrange, Act, Assert
4. **Fixtures réutilisables**: Éviter duplication du setup
5. **Tests paramétrés**: Pour tester plusieurs cas similaires
6. **Mocks avec parcimonie**: Préférer objets réels quand possible
7. **Tests rapides**: Utiliser DB en mémoire, éviter sleep()
8. **Nettoyer après soi**: pytest-django gère les transactions
9. **Tests indépendants**: Pas de dépendances entre tests
10. **Documenter les tests complexes**: Docstrings explicatives

## 🔗 Ressources

- **pytest docs**: https://docs.pytest.org/
- **pytest-django**: https://pytest-django.readthedocs.io/
- **pytest-cov**: https://pytest-cov.readthedocs.io/
- **Coverage.py**: https://coverage.readthedocs.io/
