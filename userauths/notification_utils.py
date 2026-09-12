"""Service de gestion des notifications in-app."""

from django.urls import reverse
from django.utils import timezone

from userauths.models import CustomUser, Notification


def eligible_users_queryset():
    """Utilisateurs pouvant recevoir des notifications (hors superadmin)."""
    return CustomUser.objects.filter(is_superuser=False)


def can_receive_notifications(user):
    if not user or not user.is_authenticated:
        return False
    try:
        from PB_Entreprise.models import UserProfile
        profile = UserProfile.objects.filter(user=user).first()
        if profile is not None and not profile.notif_site:
            return False
    except Exception:
        pass
    return True


def can_receive_account_notifications(user):
    return can_receive_notifications(user) and not user.is_superuser


def notify_user(
    user,
    *,
    titre,
    message,
    type_notif='info',
    lien='',
    categorie='autre',
    dedupe_key='',
    metadata=None,
    force_unread=False,
):
    """Crée ou met à jour une notification pour un utilisateur."""
    if not can_receive_notifications(user):
        return None

    payload = {
        'titre': titre,
        'message': message,
        'type_notif': type_notif,
        'lien': lien,
        'categorie': categorie,
        'metadata': metadata or {},
    }

    if dedupe_key:
        notification, created = Notification.objects.get_or_create(
            user=user,
            dedupe_key=dedupe_key,
            defaults={**payload, 'lu': False},
        )
        if not created:
            changed = any(getattr(notification, field) != payload[field] for field in payload)
            if changed or force_unread:
                for field, value in payload.items():
                    setattr(notification, field, value)
                if force_unread:
                    notification.lu = False
                notification.save()
        return notification

    return Notification.objects.create(user=user, **payload, lu=False)


def notify_account_blocked(user, *, reason='auto'):
    """Notification : compte bloqué."""
    if not can_receive_account_notifications(user):
        return None
    if reason == 'admin':
        message = (
            "Votre compte a été désactivé par un administrateur. "
            "Contactez l'administrateur pour le réactiver."
        )
    else:
        message = (
            "Votre compte a été bloqué après 3 tentatives de connexion infructueuses. "
            "Contactez l'administrateur de l'application."
        )
    return notify_user(
        user,
        titre='Compte bloqué',
        message=message,
        type_notif='compte',
        categorie='compte_bloque',
        dedupe_key='compte:bloque',
        metadata={'reason': reason, 'blocked_at': timezone.now().isoformat()},
        force_unread=True,
    )


def notify_account_password_reset(user):
    """Notification : mot de passe réinitialisé."""
    if not can_receive_account_notifications(user):
        return None
    return notify_user(
        user,
        titre='Réinitialisation du compte',
        message=(
            "Votre mot de passe a été réinitialisé avec succès. "
            "Si vous n'êtes pas à l'origine de cette action, contactez immédiatement un administrateur."
        ),
        type_notif='compte',
        categorie='compte_reset',
        dedupe_key=f'compte:reset:{timezone.now().strftime("%Y%m%d%H%M%S")}',
        metadata={'reset_at': timezone.now().isoformat()},
    )


def clear_account_blocked_notification(user):
    """Retire la notification de blocage lorsque le compte est réactivé."""
    if not user:
        return
    Notification.objects.filter(
        user=user,
        dedupe_key='compte:bloque',
    ).delete()


def _vehicules_for_user(user):
    from PB_Entreprise.models import UserProfile, Vehicule

    if user.user_type == '4':
        try:
            profile = user.profile
            categories = profile.gerant_voiture.all()
            if categories.exists():
                return Vehicule.objects.filter(category__in=categories, car_statut=True)
        except UserProfile.DoesNotExist:
            pass
        return Vehicule.objects.none()
    return Vehicule.objects.filter(car_statut=True)


def collect_vehicle_alerts(user):
    """Collecte les alertes véhicules actives pour un utilisateur."""
    from PB_Entreprise.models import (
        Assurance,
        Entretien,
        Patente,
        Stationnement,
        Vignette,
        VisiteTechnique,
    )

    alert_rules = (
        ('visite', VisiteTechnique, 'jour_restant', 32, 'Visite technique'),
        ('entretien', Entretien, 'jours_ent_restant', 3, 'Entretien'),
        ('assurance', Assurance, 'jours_assu_restant', 7, 'Assurance'),
        ('vignette', Vignette, 'jours_vign_restant', 10, 'Vignette'),
        ('patente', Patente, 'jours_pate_restant', 10, 'Patente'),
        ('stationnement', Stationnement, 'jours_cartsta_restant', 10, 'Stationnement'),
    )

    alerts = []
    lien = reverse('alerte')

    for vehicule in _vehicules_for_user(user):
        for categorie, model, attr, seuil, label in alert_rules:
            try:
                record = model.objects.filter(vehicule=vehicule).order_by('-date_saisie').first()
                if not record:
                    continue
                jours = getattr(record, attr, None)
                if jours is None or not isinstance(jours, int) or jours > seuil:
                    continue
                immat = vehicule.immatriculation
                if jours < 0:
                    message = (
                        f"L'échéance est dépassée de {abs(jours)} jour(s). "
                        f"Merci de traiter cette alerte pour le véhicule {immat}."
                    )
                else:
                    message = (
                        f"L'échéance arrive dans {jours} jour(s). "
                        f"Merci de planifier le renouvellement pour {immat}."
                    )
                alerts.append({
                    'dedupe_key': f'alert:{categorie}:{vehicule.pk}',
                    'titre': label,
                    'message': message,
                    'type_notif': 'alert',
                    'categorie': categorie,
                    'lien': lien,
                    'metadata': {
                        'jours': jours,
                        'vehicule': immat,
                        'vehicule_id': vehicule.pk,
                        'label': label,
                    },
                })
            except Exception:
                continue
    return alerts


def sync_vehicle_alerts(user):
    """Synchronise les alertes véhicules en base pour un utilisateur."""
    if not can_receive_notifications(user):
        return []

    current_alerts = collect_vehicle_alerts(user)
    current_keys = {item['dedupe_key'] for item in current_alerts}

    Notification.objects.filter(
        user=user,
        type_notif='alert',
    ).exclude(dedupe_key__in=current_keys).delete()

    for alert in current_alerts:
        notify_user(
            user,
            titre=alert['titre'],
            message=alert['message'],
            type_notif='alert',
            lien=alert['lien'],
            categorie=alert['categorie'],
            dedupe_key=alert['dedupe_key'],
            metadata=alert['metadata'],
        )

    return current_alerts


def sync_user_notifications(user):
    """Synchronise toutes les notifications dynamiques pour un utilisateur."""
    sync_vehicle_alerts(user)
    if can_receive_account_notifications(user) and not user.is_active and user.date_blocage:
        notify_account_blocked(user, reason='auto' if user.failed_login_attempts >= 3 else 'admin')


TYPE_LABELS = dict(Notification.TYPE_CHOICES)
CATEGORIE_LABELS = dict(Notification.CATEGORIE_CHOICES)


def get_notifications_queryset(user, *, unread_only=False, limit=20):
    if not can_receive_notifications(user):
        return Notification.objects.none()
    qs = Notification.objects.filter(user=user)
    if unread_only:
        qs = qs.filter(lu=False)
    return qs.order_by('-created_at')[:limit]


def serialize_notification(notification):
    meta = notification.metadata or {}
    return {
        'id': notification.id,
        'titre': notification.titre,
        'message': notification.message,
        'lien': notification.lien,
        'type_notif': notification.type_notif,
        'type_label': TYPE_LABELS.get(notification.type_notif, notification.type_notif),
        'categorie': notification.categorie,
        'categorie_label': CATEGORIE_LABELS.get(notification.categorie, notification.categorie or 'Autre'),
        'lu': notification.lu,
        'jours': meta.get('jours'),
        'vehicule': meta.get('vehicule', ''),
        'label': meta.get('label', notification.titre),
        'created_at': notification.created_at.strftime('%d/%m/%Y • %H:%M'),
        'created_at_iso': notification.created_at.isoformat(),
    }


def notifications_payload(user, *, limit=15, unread_only=False):
    empty = {'unread_count': 0, 'total_count': 0, 'notifications': []}
    if not can_receive_notifications(user):
        return empty
    sync_user_notifications(user)
    notifications = list(get_notifications_queryset(user, unread_only=unread_only, limit=limit))
    unread_count = Notification.objects.filter(user=user, lu=False).count()
    return {
        'unread_count': unread_count,
        'total_count': unread_count if unread_only else len(notifications),
        'notifications': [serialize_notification(n) for n in notifications],
    }


def notifications_inbox_payload(user, *, status='', categorie='', selected_id=None, limit=80):
    empty = {
        'ok': True,
        'unread_count': 0,
        'stats': {'total': 0, 'non_lues': 0, 'lues': 0, 'alertes': 0},
        'notifications': [],
        'selected': None,
    }
    if not can_receive_notifications(user):
        return empty
    sync_user_notifications(user)
    qs = Notification.objects.filter(user=user)
    stats = {
        'total': qs.count(),
        'non_lues': qs.filter(lu=False).count(),
        'lues': qs.filter(lu=True).count(),
        'alertes': qs.filter(type_notif='alert').count(),
    }
    filtered = qs
    if status == 'unread':
        filtered = filtered.filter(lu=False)
    elif status == 'read':
        filtered = filtered.filter(lu=True)
    elif status == 'alert':
        filtered = filtered.filter(type_notif='alert')
    if categorie:
        filtered = filtered.filter(categorie=categorie)
    items = [serialize_notification(n) for n in filtered.order_by('-created_at')[:limit]]
    selected = None
    if selected_id:
        try:
            selected = serialize_notification(
                Notification.objects.get(user=user, pk=int(selected_id))
            )
        except (Notification.DoesNotExist, TypeError, ValueError):
            selected = None
    return {
        'ok': True,
        'unread_count': stats['non_lues'],
        'stats': stats,
        'notifications': items,
        'selected': selected,
    }


def mark_notification_read(user, notification_id):
    updated = Notification.objects.filter(user=user, pk=notification_id, lu=False).update(lu=True)
    return updated > 0


def mark_notification_unread(user, notification_id):
    updated = Notification.objects.filter(user=user, pk=notification_id, lu=True).update(lu=False)
    return updated > 0


def mark_all_notifications_read(user):
    return Notification.objects.filter(user=user, lu=False).update(lu=True)
