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

**Localisation**: [django_app_parameter/managers.py](django_app_parameter/managers.py)

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
```

**Avantages**:
- Encapsule la logique métier
- Gestion d'erreur cohérente
- Retourne l'objet Parameter complet pour utiliser `get()` et `set()`

### 3. Proxy Classes - Typed Parameter Models

**Localisation**: [django_app_parameter/models.py](django_app_parameter/models.py)

**Usage**: Sous-classes proxy pour chaque type de paramètre

```python
class Parameter(models.Model):
    """Modèle de base avec get() et set()"""

    def get(self) -> Any:
        """Retourne la valeur convertie au type natif"""
        str_value = self._get_decrypted_value(self.value)
        return self._cast_from_str(str_value)

    def set(self, new_value: Any, auto_cast: bool = False) -> None:
        """Définit la valeur avec validation de type"""
        if auto_cast:
            new_value = self._cast_from_str(new_value)
        if not self._is_instance(new_value):
            raise ParameterValueTypeError(...)
        self._run_validators(new_value)
        self.value = self._cast_to_str(new_value)
        self.save()

class ParameterInt(Parameter):
    """Proxy pour paramètres entiers"""
    class Meta:
        proxy = True

    def _cast_from_str(self, value: str) -> int:
        return int(value)

    def _is_instance(self, value: Any) -> bool:
        return isinstance(value, int)
```

**Avantages**:
- Chaque type a sa propre classe avec logique de conversion
- `from_db()` retourne automatiquement la bonne sous-classe
- `get()` et `set()` fonctionnent pour tous les types
- `auto_cast` permet de convertir depuis string facilement

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

**Pourquoi**: Éviter conflits avec noms de classes/méthodes

```python
# En haut du fichier models.py
_str = str
_list = list
_dict = dict
_bool = bool
_int = int
_float = float

# Utilisation dans les sous-classes
class ParameterInt(Parameter):
    def _cast_from_str(self, value: _str) -> _int:
        return _int(value)

class ParameterList(Parameter):
    def _cast_from_str(self, value: _str) -> _list[_str]:
        return [item.strip() for item in value.split(",")]
```

### Type hints complets

**Standard**: Type hints sur toutes les signatures publiques

```python
from typing import Any
from decimal import Decimal

class ParameterDecimal(Parameter):
    """Proxy pour paramètres Decimal"""

    def _cast_from_str(self, value: _str) -> Decimal:
        return Decimal(value)

    def _is_instance(self, value: Any) -> bool:
        return isinstance(value, Decimal)

# Usage
param = Parameter.objects.get(slug="TAX_RATE")
value = param.get()  # Returns Decimal
param.set(Decimal("19.6"))  # Accepts Decimal
param.set("19.6", auto_cast=True)  # Converts string to Decimal
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

# Type incorrect dans set()
from django_app_parameter.models import ParameterValueTypeError

def set(self, new_value: Any, auto_cast: bool = False) -> None:
    if auto_cast:
        new_value = self._cast_from_str(new_value)
    if not self._is_instance(new_value):
        raise ParameterValueTypeError(
            f"Invalid type, expected {self.get_type()} "
            f"got {type(new_value).__name__}"
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

    Note: Les valeurs sont retournées dans leur type natif (int, bool, etc.).
    """
    return {
        param.slug: param.get()
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
        if self.instance.value_type == TYPES.BOO:
            self.fields['value'] = forms.BooleanField(
                required=False,
                initial=self.instance.get()
            )
        elif self.instance.value_type == TYPES.INT:
            self.fields['value'] = forms.IntegerField(
                initial=self.instance.get()
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
        value_type=TYPES.STR,
        value="test value"
    )

@pytest.fixture
def int_parameter_with_validators(db):
    """Paramètre int avec validateurs"""
    param = Parameter.objects.create(
        name="Test Int",
        value_type=TYPES.INT,
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
    (TYPES.INT, "42", 42),
    (TYPES.FLT, "3.14", 3.14),
    (TYPES.BOO, "true", True),
    (TYPES.LST, "a,b,c", ["a", "b", "c"]),
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

1. **Ajouter le type dans constants.py**:
```python
class TYPES(models.TextChoices):
    # ... existants
    IPV = "IPV", "IPv4 Address"  # Nouveau type
```

2. **Créer la classe proxy dans models.py**:
```python
class ParameterIpv4(Parameter):
    """Proxy model for IPv4 address parameters."""

    type = TYPES.IPV

    class Meta:
        proxy = True

    def _cast_from_str(self, value: _str) -> _str:
        """Validate and return IPv4 address."""
        from django.core.validators import validate_ipv4_address
        validate_ipv4_address(value.strip())
        return value.strip()

    def _is_instance(self, value: Any) -> bool:
        """Check if value is a valid IPv4 string."""
        if not isinstance(value, str):
            return False
        from django.core.validators import validate_ipv4_address
        try:
            validate_ipv4_address(value)
            return True
        except ValidationError:
            return False
```

3. **Enregistrer dans managers.py**:
```python
def get_proxy_class(value_type: str) -> type:
    """Return the proxy class for a given value_type."""
    from django_app_parameter.models import (
        # ... existants
        ParameterIpv4,
    )
    mapping = {
        # ... existants
        TYPES.IPV: ParameterIpv4,
    }
    return mapping.get(value_type, Parameter)
```

4. **Créer migration**:
```bash
poetry run python manage.py makemigrations django_app_parameter
```

5. **Ajouter champ dans admin.py**:
```python
class ParameterEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ... autres types
        elif self.instance.value_type == TYPES.IPV:
            self.fields['value'] = forms.GenericIPAddressField(
                protocol='IPv4',
                initial=self.instance.get()
            )
```

6. **Ajouter tests**:
```python
# Dans tests/test_django_app_parameter.py
def test_ipv4_parameter(db):
    param = Parameter.objects.create(
        name="Server IP",
        value_type=TYPES.IPV,
        value="192.168.1.1"
    )
    assert param.get() == "192.168.1.1"

def test_set_ipv4(db):
    param = Parameter.objects.create(
        name="Server IP",
        value_type=TYPES.IPV,
        value="192.168.1.1"
    )
    param.set("10.0.0.1")
    param.refresh_from_db()
    assert param.value == "10.0.0.1"

def test_set_invalid_ipv4(db):
    param = Parameter.objects.create(
        name="Server IP",
        value_type=TYPES.IPV,
        value="192.168.1.1"
    )
    with pytest.raises(ParameterValueTypeError):
        param.set("999.999.999.999")
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
