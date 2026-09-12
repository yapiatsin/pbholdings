"""Validation des dates de saisie : année en cours et les 4 années précédentes."""
from datetime import date, datetime

from django import forms
from django.utils import timezone

# Écart maximal autorisé entre l'année de la date min et celle de la date max.
SAISIE_WINDOW_YEARS = 4


def saisie_today():
    return timezone.localdate()


def saisie_min_date():
    """Date minimale de saisie : 1er janvier de (année en cours - 4).

    La date maximale restant aujourd'hui, la fenêtre de saisie couvre l'année
    en cours et les 4 années précédentes (ex. en 2026 : du 01/01/2022 à ce jour).
    """
    return date(saisie_today().year - SAISIE_WINDOW_YEARS, 1, 1)


def saisie_datetime_local_min():
    """Valeur min pour les champs HTML datetime-local."""
    return saisie_min_date().strftime('%Y-%m-%dT00:00')


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


def is_saisie_date_too_old(value):
    parsed = coerce_to_date(value)
    if parsed is None:
        return False
    return parsed < saisie_min_date()


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


def validate_saisie_date_not_too_old(value, label='La date'):
    parsed = coerce_to_date(value)
    if parsed is None:
        return value
    minimum = saisie_min_date()
    if parsed < minimum:
        raise forms.ValidationError(
            f'{label} ne peut pas être antérieure au {minimum.strftime("%d/%m/%Y")}.'
        )
    return value


def apply_widget_max_past_date(field):
    widget = field.widget
    input_type = widget.attrs.get('type') or getattr(widget, 'input_type', None)
    if input_type == 'datetime-local':
        widget.attrs['max'] = saisie_datetime_local_max()
    else:
        widget.attrs['max'] = saisie_today().isoformat()


def apply_widget_min_date(field):
    widget = field.widget
    input_type = widget.attrs.get('type') or getattr(widget, 'input_type', None)
    if input_type == 'datetime-local':
        widget.attrs['min'] = saisie_datetime_local_min()
    else:
        widget.attrs['min'] = saisie_min_date().isoformat()


class SaisiePastDateMixin:
    """Borne les champs listés à la fenêtre de saisie autorisée.

    Chaque champ de `saisie_past_date_fields` reçoit la borne haute (aujourd'hui)
    et la borne basse (`saisie_min_date`), côté widget HTML (`min` / `max`) comme
    côté serveur. `saisie_min_date_fields` permet de restreindre la borne basse à
    d'autres champs — ou de la désactiver avec un tuple vide.
    """

    saisie_past_date_fields = ()
    saisie_min_date_fields = None  # None => mêmes champs que saisie_past_date_fields
    saisie_past_date_labels = {}

    def _saisie_min_fields(self):
        if self.saisie_min_date_fields is None:
            return self.saisie_past_date_fields
        return self.saisie_min_date_fields

    def _saisie_field_label(self, name):
        label = self.saisie_past_date_labels.get(name)
        if not label:
            label = self.fields[name].label or name.replace('_', ' ')
        return label

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.saisie_past_date_fields:
            if name in self.fields:
                apply_widget_max_past_date(self.fields[name])
        for name in self._saisie_min_fields():
            if name in self.fields:
                apply_widget_min_date(self.fields[name])

    def clean(self):
        cleaned_data = super().clean()
        for name in self.saisie_past_date_fields:
            if name not in cleaned_data:
                continue
            validate_saisie_date_not_future(cleaned_data[name], self._saisie_field_label(name))
        for name in self._saisie_min_fields():
            if name not in cleaned_data:
                continue
            validate_saisie_date_not_too_old(cleaned_data[name], self._saisie_field_label(name))
        return cleaned_data
