from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .utils import invalid_str

def validate_special_char(value):
    if invalid_str(value):
        raise ValidationError(
            _('%(value)s contains special characters'),
            params={'value': value},
        )