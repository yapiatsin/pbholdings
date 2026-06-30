"""Validation des dates de saisie : passé et aujourd'hui uniquement."""
from datetime import date, datetime

from django import forms
from django.utils import timezone


def saisie_today():
    return timezone.localdate()


def saisie_datetime_local_max():
    """Valeur max pour les champs HTML datetime-local (jusqu'à maintenant)."""
    return timezone.localtime().replace(second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M')


def coerce_to_date(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None


def is_saisie_date_allowed(value):
    parsed = coerce_to_date(value)
    if parsed is None:
        return False
    return parsed <= saisie_today()


def validate_saisie_date_not_future(value, label='La date'):
    parsed = coerce_to_date(value)
    if parsed is None:
        return value
    today = saisie_today()
    if parsed > today:
        raise forms.ValidationError(
            f'{label} ne peut pas être postérieure au {today.strftime("%d/%m/%Y")}.'
        )
    return value


def apply_widget_max_past_date(field):
    widget = field.widget
    input_type = widget.attrs.get('type') or getattr(widget, 'input_type', None)
    if input_type == 'datetime-local':
        widget.attrs['max'] = saisie_datetime_local_max()
    else:
        widget.attrs['max'] = saisie_today().isoformat()


class SaisiePastDateMixin:
    """Limite les champs listés aux dates passées ou au jour courant."""

    saisie_past_date_fields = ()
    saisie_past_date_labels = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.saisie_past_date_fields:
            if name in self.fields:
                apply_widget_max_past_date(self.fields[name])

    def clean(self):
        cleaned_data = super().clean()
        for name in self.saisie_past_date_fields:
            if name not in cleaned_data:
                continue
            label = self.saisie_past_date_labels.get(name)
            if not label:
                label = self.fields[name].label or name.replace('_', ' ')
            validate_saisie_date_not_future(cleaned_data[name], label)
        return cleaned_data
