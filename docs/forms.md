# Forms

## Résumé du système de formulaires

Le module `django_app_parameter.forms` expose un système flexible pour créer des champs de formulaire adaptés au type de chaque paramètre.

## API principale

### create_parameter_field(parameter, **kwargs) → forms.Field

Fonction factory qui crée le bon champ Django selon le type du paramètre.

```python
from django_app_parameter.forms import create_parameter_field
from django_app_parameter.models import Parameter

param = Parameter.objects.get(slug="max-retries")
field = create_parameter_field(param)
# → IntegerField si param.value_type == "INT"

# Avec options personnalisées
field = create_parameter_field(param, required=True, help_text="Custom")
```

## Configuration par type

| Type | Field Django | Widget | Options |
|------|--------------|--------|---------|
| STR | CharField | - | - |
| INT | IntegerField | - | - |
| FLT | FloatField | - | - |
| DCL | DecimalField | - | - |
| BOO | BooleanField | - | - |
| DATE | DateField | - | - |
| DATETIME | DateTimeField | - | - |
| TIME | TimeField | - | - |
| URL | URLField | - | - |
| EMAIL | EmailField | - | - |
| PATH | CharField | - | - |
| JSN | CharField | Textarea | - |
| DICT | CharField | Textarea | - |
| LIST | CharField | - | help_text |
| DURATION | FloatField | - | help_text |
| PERCENTAGE | FloatField | - | min=0, max=100 |

## Exemple d'utilisation dans un formulaire custom

```python
from django import forms
from django_app_parameter.forms import create_parameter_field
from django_app_parameter.models import Parameter

class SettingsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for param in Parameter.objects.filter(is_global=True):
            self.fields[param.slug] = create_parameter_field(param)
```

## Extension du registre

```python
from django_app_parameter.forms import FIELD_TYPE_REGISTRY, FieldConfig
from django import forms

FIELD_TYPE_REGISTRY["MY_CUSTOM_TYPE"] = FieldConfig(
    field_class=forms.CharField,
    widget=forms.Textarea(attrs={"rows": 10}),
    extra_kwargs={"max_length": 500},
    help_text="Mon type personnalisé",
)
```

## Formulaires Admin fournis

| Classe | Usage |
|--------|-------|
| ParameterCreateForm | Création d'un paramètre (sans champ value) |
| ParameterEditForm | Édition d'un paramètre (avec validation) |
| ParameterValidatorForm | Gestion des validateurs |
