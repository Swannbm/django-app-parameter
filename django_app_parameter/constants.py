from django.db.models import TextChoices


class TYPES(TextChoices):
    """Enumeration of supported parameter value types."""

    INT = "INT", "Nombre entier"
    STR = "STR", "Chaîne de caractères"
    FLT = "FLT", "Nombre à virgule (Float)"
    DCL = "DCL", "Nombre à virgule (Decimal)"
    JSN = "JSN", "JSON"
    BOO = "BOO", "Booléen"
    DATE = "DAT", "Date (YYYY-MM-DD)"
    DATETIME = "DTM", "Date et heure (ISO 8601)"
    TIME = "TIM", "Heure (HH:MM:SS)"
    URL = "URL", "URL validée"
    EMAIL = "EML", "Email validé"
    LIST = "LST", "Liste (séparée par virgules)"
    DICT = "DCT", "Dictionnaire JSON"
    PATH = "PTH", "Chemin de fichier"
    DURATION = "DUR", "Durée (en secondes)"
    PERCENTAGE = "PCT", "Pourcentage (0-100)"
