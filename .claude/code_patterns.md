# Patterns de code et conventions

## 🎯 Patterns d'architecture

### 1. Proxy Pattern - AccessParameter

**Localisation**: [django_app_parameter/__init__.py](django_app_parameter/__init__.py)

**Usage**: Fournir un accès similaire à Django settings

```python
class AccessParameter:
    """Proxy pour accéder aux paramètres comme Django settings"""

    def __getattr__(self, slug: str):
        param = Parameter.objects.get_from_slug(slug)
        return param.get()

# Export global
app_parameter = AccessParameter()

# Utilisation
from django_app_parameter import app_parameter
title = app_parameter.BLOG_TITLE  # Auto-converti au bon type
```

**Avantages**:
- API simple et intuitive
- Conversion automatique de type
- Cohérent avec les conventions Django

### 2. Manager Pattern - ParameterManager

**Localisation**: [django_app_parameter/models.py](django_app_parameter/models.py)

**Usage**: Étendre Django Manager avec méthodes spécifiques au domaine

```python
class ParameterManager(models.Manager):
    """Manager personnalisé avec méthodes métier"""

    def get_from_slug(self, slug: str) -> "Parameter":
        """Récupère ou lève ImproperlyConfigured"""
        try:
            return self.get(slug=slug)
        except self.model.DoesNotExist:
            raise ImproperlyConfigured(f"Parameter {slug} not found")

    def int(self, slug: str) -> int:
        """Raccourci pour récupérer un entier"""
        return self.get_from_slug(slug).int()

    # ... autres méthodes typées
```

**Avantages**:
- Encapsule la logique métier
- Fournit des raccourcis typés
- Gestion d'erreur cohérente

### 3. Strategy Pattern - Conversion de types

**Localisation**: [django_app_parameter/models.py](django_app_parameter/models.py) (`get()` et `set()`)

**Usage**: Dispatch basé sur dictionnaire pour conversion de types

```python
def get(self) -> ParameterReturnType:
    """Conversion automatique selon value_type"""
    functions = {
        self.TYPES.INT: "int",
        self.TYPES.STR: "str",
        self.TYPES.FLT: "float",
        self.TYPES.DCL: "decimal",
        # ... autres mappings
    }
    method_name = functions[self.value_type]
    return getattr(self, method_name)()

def set(self, value: ParameterAcceptType) -> None:
    """Route vers le bon setter selon value_type"""
    setters = {
        self.TYPES.INT: self.set_int,
        self.TYPES.STR: self.set_str,
        # ... autres mappings
    }
    setter_func = setters[self.value_type]
    setter_func(value)
```

**Avantages**:
- Évite les chaînes if/elif
- Facile à étendre avec nouveaux types
- Mapping clair et maintenable

### 4. Registry Pattern - Validateurs

**Localisation**: [django_app_parameter/utils.py](django_app_parameter/utils.py)

**Usage**: Registre centralisé pour validateurs intégrés et personnalisés

```python
# Validateurs intégrés
BUILTIN_VALIDATORS = {
    "min_value": MinValueValidator,
    "max_value": MaxValueValidator,
    "min_length": MinLengthValidator,
    # ... autres validateurs
}

def get_validator_from_registry(validator_type: str):
    """Lookup avec cache"""
    # 1. Vérifier les built-in
    if validator_type in BUILTIN_VALIDATORS:
        return BUILTIN_VALIDATORS[validator_type]

    # 2. Vérifier les customs dans settings
    custom_validators = get_setting("validators", {})
    if validator_type in custom_validators:
        return import_validator(custom_validators[validator_type])

    raise ValueError(f"Unknown validator: {validator_type}")
```

**Avantages**:
- Point central de vérité pour validateurs
- Support intégrés et personnalisés
- Import lazy avec cache

### 5. Factory Pattern - ParameterValidator

**Localisation**: [django_app_parameter/models.py](django_app_parameter/models.py) (`ParameterValidator.get_validator()`)

**Usage**: Instanciation de validateurs depuis configuration

```python
class ParameterValidator(models.Model):
    validator_type = models.CharField(max_length=400)
    validator_params = models.JSONField(default=dict)

    def get_validator(self):
        """Factory: crée validateur depuis config"""
        validator_class = get_validator_from_registry(self.validator_type)

        # Support fonction et classe
        if callable(validator_class) and not inspect.isclass(validator_class):
            return validator_class

        # Instanciation avec paramètres
        return validator_class(**self.validator_params)
```

**Avantages**:
- Sépare création et utilisation
- Configuration déclarative
- Flexible (fonction ou classe)

## 🔧 Conventions de code

### Aliasing de types built-in

**Pourquoi**: Éviter conflits avec noms de méthodes

```python
# En haut du fichier models.py
_str = str
_list = list
_dict = dict
_bool = bool
_int = int
_float = float

# Utilisation
def str(self) -> _str:
    """Méthode nommée 'str' mais retourne type 'str'"""
    return _str(self.value)

def list(self) -> _list[_str]:
    """Retourne une liste Python native"""
    return self.value.split(",")
```

### Type hints complets

**Standard**: Type hints sur toutes les signatures publiques

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal
    from datetime import date, datetime, time, timedelta
    from pathlib import Path

def decimal(self) -> "Decimal":
    """Type hint conditionnel pour éviter imports runtime"""
    from decimal import Decimal
    return Decimal(self.value)

def set_decimal(self, value: "Decimal") -> None:
    """Setter avec vérification de type"""
    from decimal import Decimal
    if not isinstance(value, Decimal):
        raise TypeError(f"Expected Decimal, got {type(value)}")
    self.value = _str(value)
    self._run_validators()
    self.save()
```

### Gestion d'erreurs cohérente

**Convention**: Utiliser les exceptions Django/Python standards

```python
# Paramètre manquant
from django.core.exceptions import ImproperlyConfigured

def get_from_slug(self, slug: str) -> "Parameter":
    try:
        return self.get(slug=slug)
    except self.model.DoesNotExist:
        raise ImproperlyConfigured(
            f"Parameter '{slug}' does not exist. "
            f"Please create it in Django admin."
        )

# Conversion invalide
def int(self) -> _int:
    try:
        return _int(self.value)
    except ValueError as e:
        raise ValueError(
            f"Cannot convert '{self.value}' to int for parameter '{self.slug}'"
        ) from e

# Type incorrect dans setter
def set_int(self, value: _int) -> None:
    if not isinstance(value, _int):
        raise TypeError(
            f"Expected int, got {type(value).__name__} "
            f"for parameter '{self.slug}'"
        )
```

### Logging

**Convention**: Logger au niveau module

```python
import logging

logger = logging.getLogger(__name__)

# Utilisation
logger.debug(f"Loading parameter: {slug}")
logger.info(f"Created parameter: {self.slug}")
logger.warning(f"Parameter {slug} not found, using default")
logger.error(f"Validation failed for {self.slug}: {e}")
```

### Docstrings

**Format**: Style Google/NumPy

```python
def load_from_json(self, data: list[dict], do_update: bool = True) -> None:
    """Import parameters from JSON data.

    Args:
        data: List of parameter dictionaries with keys:
            - name (required): Parameter name
            - value (required): Parameter value as string
            - value_type (optional): Type code (defaults to STR)
            - description (optional): Description text
            - is_global (optional): Global flag (defaults to False)
            - validators (optional): List of validator configs
        do_update: If True, update existing parameters. If False, skip existing.

    Raises:
        ValueError: If required keys are missing
        ValidationError: If validators fail

    Example:
        >>> data = [
        ...     {
        ...         "name": "Site Title",
        ...         "value": "My Blog",
        ...         "value_type": "STR",
        ...         "is_global": True
        ...     }
        ... ]
        >>> Parameter.objects.load_from_json(data)
    """
```

## 🎨 Patterns spécifiques à l'application

### Génération de slug

**Localisation**: [django_app_parameter/models.py](django_app_parameter/models.py)

**Pattern**: Slugification personnalisée pour paramètres

```python
def parameter_slugify(s: str) -> str:
    """Convertit nom en slug UPPER_SNAKE_CASE"""
    return slugify(s).replace("-", "_").upper()

# Dans le modèle
def save(self, *args, **kwargs):
    if not self.slug:
        self.slug = parameter_slugify(self.name)
    super().save(*args, **kwargs)
```

**Exemples**:
- `"Blog Title"` → `"BLOG_TITLE"`
- `"Max Upload Size (MB)"` → `"MAX_UPLOAD_SIZE_MB"`
- `"API v2 Endpoint"` → `"API_V2_ENDPOINT"`

### Context Processor pour templates

**Localisation**: [django_app_parameter/context_processors.py](django_app_parameter/context_processors.py)

**Pattern**: Injection de paramètres globaux dans contexte de template

```python
def add_global_parameter_context(request):
    """Ajoute tous les paramètres globaux au contexte.

    Note: Les valeurs sont toujours en string pour simplicité.
    Pour typage fort, utiliser app_parameter dans les vues.
    """
    return {
        param.slug: param.str()
        for param in Parameter.objects.filter(is_global=True)
    }
```

**Configuration dans settings.py**:
```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ... autres processors
                'django_app_parameter.context_processors.add_global_parameter_context',
            ],
        },
    },
]
```

### Admin customization

**Localisation**: [django_app_parameter/admin.py](django_app_parameter/admin.py)

**Pattern**: Formulaires différents pour création vs édition

```python
class ParameterAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        """Route vers bon formulaire selon contexte"""
        if obj is None:  # Création
            kwargs['form'] = ParameterCreateForm
        else:  # Édition
            kwargs['form'] = ParameterEditForm
        return super().get_form(request, obj, **kwargs)

class ParameterEditForm(forms.ModelForm):
    """Formulaire avec champ de valeur dynamique"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customiser le champ selon value_type
        if self.instance.value_type == Parameter.TYPES.BOO:
            self.fields['value'] = forms.BooleanField(
                required=False,
                initial=self.instance.bool()
            )
        elif self.instance.value_type == Parameter.TYPES.INT:
            self.fields['value'] = forms.IntegerField(
                initial=self.instance.int()
            )
        # ... autres types
```

### Import/Export JSON

**Pattern**: Format JSON standardisé pour paramètres

```json
[
    {
        "name": "Site Title",
        "slug": "SITE_TITLE",
        "value": "My Awesome Site",
        "value_type": "STR",
        "description": "Main site title displayed in header",
        "is_global": true,
        "validators": [
            {
                "validator_type": "min_length",
                "validator_params": {"limit_value": 3}
            },
            {
                "validator_type": "max_length",
                "validator_params": {"limit_value": 100}
            }
        ]
    }
]
```

**Utilisation**:
```bash
# Export
python manage.py dump_param parameters.json --indent 2

# Import (crée ou met à jour)
python manage.py load_param --file parameters.json

# Import sans mise à jour des existants
python manage.py load_param --file parameters.json --no-update
```

## 🧪 Patterns de tests

### Fixtures réutilisables

```python
import pytest
from django_app_parameter.models import Parameter

@pytest.fixture
def string_parameter(db):
    """Paramètre string basique"""
    return Parameter.objects.create(
        name="Test String",
        value_type=Parameter.TYPES.STR,
        value="test value"
    )

@pytest.fixture
def int_parameter_with_validators(db):
    """Paramètre int avec validateurs"""
    param = Parameter.objects.create(
        name="Test Int",
        value_type=Parameter.TYPES.INT,
        value="42"
    )
    param.parametervalidator_set.create(
        validator_type="min_value",
        validator_params={"limit_value": 0}
    )
    param.parametervalidator_set.create(
        validator_type="max_value",
        validator_params={"limit_value": 100}
    )
    return param
```

### Tests paramétrés pour types

```python
import pytest

@pytest.mark.parametrize("value_type,value,expected", [
    (Parameter.TYPES.INT, "42", 42),
    (Parameter.TYPES.FLT, "3.14", 3.14),
    (Parameter.TYPES.BOO, "true", True),
    (Parameter.TYPES.LST, "a,b,c", ["a", "b", "c"]),
])
def test_parameter_conversion(db, value_type, value, expected):
    """Test conversion pour tous les types"""
    param = Parameter.objects.create(
        name="Test",
        value_type=value_type,
        value=value
    )
    assert param.get() == expected
```

### Tests d'admin avec Django test client

```python
import pytest
from django.contrib.auth.models import User

@pytest.fixture
def admin_client(db, client):
    """Client authentifié en tant qu'admin"""
    user = User.objects.create_superuser(
        username="admin",
        email="admin@test.com",
        password="admin"
    )
    client.force_login(user)
    return client

def test_admin_change_view(admin_client, string_parameter):
    """Test accès à la vue de modification"""
    url = f"/admin/django_app_parameter/parameter/{string_parameter.pk}/change/"
    response = admin_client.get(url)
    assert response.status_code == 200
    assert "Test String" in response.content.decode()
```

## 🚀 Patterns d'extension

### Ajouter un nouveau type de données

**Checklist complète**:

1. **Ajouter le type dans models.py**:
```python
class Parameter(models.Model):
    class TYPES(models.TextChoices):
        # ... existants
        IPV = "IPV", "IPv4 Address"  # Nouveau type

    VALUE_TYPE_CHOICES = [
        # ... existants
        (TYPES.IPV, "IPv4 Address"),
    ]
```

2. **Ajouter getter**:
```python
def ipv4(self) -> _str:
    """Retourne adresse IPv4 validée"""
    from django.core.validators import validate_ipv4_address
    validate_ipv4_address(self.value)
    return self.value
```

3. **Ajouter setter**:
```python
def set_ipv4(self, value: _str) -> None:
    """Définit adresse IPv4 avec validation"""
    from django.core.validators import validate_ipv4_address
    if not isinstance(value, _str):
        raise TypeError(f"Expected str, got {type(value)}")
    validate_ipv4_address(value)  # Valide avant de stocker
    self.value = value
    self._run_validators()
    self.save()
```

4. **Mettre à jour get() et set()**:
```python
def get(self) -> ParameterReturnType:
    functions = {
        # ... existants
        self.TYPES.IPV: "ipv4",
    }
    # ...

def set(self, value: ParameterAcceptType) -> None:
    setters = {
        # ... existants
        self.TYPES.IPV: self.set_ipv4,
    }
    # ...
```

5. **Ajouter méthode au Manager**:
```python
class ParameterManager(models.Manager):
    def ipv4(self, slug: str) -> _str:
        return self.get_from_slug(slug).ipv4()
```

6. **Créer migration**:
```bash
cd demo_project
poetry run python manage.py makemigrations django_app_parameter
```

7. **Ajouter champ dans admin.py**:
```python
class ParameterEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ... autres types
        elif self.instance.value_type == Parameter.TYPES.IPV:
            self.fields['value'] = forms.GenericIPAddressField(
                protocol='IPv4',
                initial=self.instance.ipv4()
            )
```

8. **Ajouter tests**:
```python
# Dans tests/test_django_app_parameter.py
def test_ipv4_parameter(db):
    param = Parameter.objects.create(
        name="Server IP",
        value_type=Parameter.TYPES.IPV,
        value="192.168.1.1"
    )
    assert param.ipv4() == "192.168.1.1"
    assert param.get() == "192.168.1.1"

def test_set_ipv4(db):
    param = Parameter.objects.create(
        name="Server IP",
        value_type=Parameter.TYPES.IPV,
        value="192.168.1.1"
    )
    param.set_ipv4("10.0.0.1")
    param.refresh_from_db()
    assert param.value == "10.0.0.1"

def test_set_invalid_ipv4(db):
    param = Parameter.objects.create(
        name="Server IP",
        value_type=Parameter.TYPES.IPV,
        value="192.168.1.1"
    )
    with pytest.raises(ValidationError):
        param.set_ipv4("999.999.999.999")
```

### Ajouter un validateur personnalisé

**Dans votre projet Django**:

1. **Créer le validateur** (ex: `myapp/validators.py`):
```python
from django.core.exceptions import ValidationError

def validate_even_number(value):
    """Validateur fonction simple"""
    if int(value) % 2 != 0:
        raise ValidationError(
            f"{value} n'est pas un nombre pair",
            code='not_even'
        )

class MultipleOfValidator:
    """Validateur classe avec paramètre"""
    def __init__(self, multiple_of):
        self.multiple_of = multiple_of

    def __call__(self, value):
        if int(value) % self.multiple_of != 0:
            raise ValidationError(
                f"{value} n'est pas un multiple de {self.multiple_of}",
                code='not_multiple'
            )
```

2. **Déclarer dans settings.py**:
```python
DJANGO_APP_PARAMETER = {
    'validators': {
        'even_number': 'myapp.validators.validate_even_number',
        'multiple_of': 'myapp.validators.MultipleOfValidator',
    }
}
```

3. **Utiliser dans l'admin ou via code**:
```python
# Via l'admin: ajouter inline validator avec type "even_number"

# Via code
param = Parameter.objects.get(slug="MY_NUMBER")
param.parametervalidator_set.create(
    validator_type="multiple_of",
    validator_params={"multiple_of": 5}
)
```

## 📚 Références

- **Design Patterns**: [Refactoring Guru](https://refactoring.guru/design-patterns)
- **Django Best Practices**: [Django Best Practices](https://django-best-practices.readthedocs.io/)
- **Python Type Hints**: [PEP 484](https://peps.python.org/pep-0484/)
