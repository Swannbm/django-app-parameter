import json

from decimal import Decimal

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.text import slugify


def parameter_slugify(content):
    """
    Transform content :
    * slugify (with django's function)
    * upperise
    * replace dash (-) with underscore (_)
    """
    return slugify(content).upper().replace("-", "_")


class ParameterManager(models.Manager):
    def get_from_slug(self, slug):
        """Send ImproperlyConfigured exception if parameter is not in DB"""
        try:
            return super().get(slug=slug)
        except Parameter.DoesNotExist as e:
            raise ImproperlyConfigured(f"{slug} parameters need to be set") from e

    def int(self, slug):
        return self.get_from_slug(slug).int()

    def float(self, slug):
        return self.get_from_slug(slug).float()

    def str(self, slug):
        return self.get_from_slug(slug).str()

    def decimal(self, slug):
        return self.get_from_slug(slug).decimal()

    def json(self, slug):
        return self.get_from_slug(slug).json()

    def create_or_update(self, parameter, update=True):
        # add slug if not set
        if "slug" not in parameter:
            parameter["slug"] = parameter_slugify(parameter["name"])
        try:
            param = Parameter.objects.get(slug=parameter["slug"])
            result = "Already exists"
            if update:
                param.name = parameter["name"]
                param.value = parameter.get("value", "")
                param.value_type = parameter.get("value_type", Parameter.TYPES.STR)
                param.is_global = parameter.get("is_global", False)
                param.description = parameter.get("description", "")
                param.save()
                result += ", updated"
            return result
        except Parameter.DoesNotExist:
            param = Parameter(**parameter)
            param.save()
            return "Added"


class Parameter(models.Model):

    objects = ParameterManager()

    class TYPES(models.TextChoices):
        INT = "INT", "Nombre entier"
        STR = "STR", "Chaîne de caractères"
        FLT = "FLT", "Nombre à virgule (Float)"
        DCL = "DCL", "Nombre à virgule (Decimal)"
        JSN = "JSN", "JSON"

    name = models.CharField("Nom", max_length=100)
    slug = models.SlugField(max_length=40, unique=True)
    value_type = models.CharField(
        "Type de donnée", max_length=3, choices=TYPES.choices, default=TYPES.STR
    )
    description = models.TextField("Description", blank=True)
    value = models.CharField("Valeur", max_length=250)
    is_global = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = parameter_slugify(self.name)
        super().save(*args, **kwargs)

    def get(self):
        """Return parameter value casted accordingly to its value_type"""
        functions = {
            self.TYPES.INT: "int",
            self.TYPES.STR: "str",
            self.TYPES.FLT: "float",
            self.TYPES.DCL: "decimal",
            self.TYPES.JSN: "json",
        }
        function_name = functions[self.value_type]
        return getattr(self, function_name)()

    def int(self):
        """Return parameter value casted as int()"""
        return int(self.value)

    def str(self):
        """Return parameter value casted as str()"""
        return str(self.value)

    def float(self):
        """Return parameter value casted as float()"""
        return float(self.value)

    def decimal(self):
        """Return parameter value casted as Decimal()"""
        return Decimal(self.value)

    def json(self):
        """Return parameter value casted as dict() using json lib"""
        return json.loads(self.value)

    def __str__(self):
        return self.name
