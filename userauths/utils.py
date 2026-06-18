import logging
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from django.conf import settings
from django.core.mail import get_connection
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

LOGO_CID = 'pb_logo'


def _logo_path():
    return Path(settings.BASE_DIR) / 'static' / 'pb_site_asset' / 'img' / 'logo' / 'new_logo.png'


def _site_base_url():
    """Base URL absolue (sans slash final) pour les liens dans les emails."""
    return (
        getattr(settings, 'FRONTEND_URL', None)
        or getattr(settings, 'SITE_URL', None)
        or 'http://127.0.0.1:8004'
    ).rstrip('/')


def _login_url():
    return _site_base_url() + reverse('login')


def _activation_url(token):
    return _site_base_url() + reverse('verify-email', kwargs={'token': token})


def create_email_verification_token(user):
    from userauths.models import EmailVerificationToken

    EmailVerificationToken.objects.filter(
        user=user,
        used=False,
    ).update(used=True, used_at=timezone.now())
    return EmailVerificationToken.objects.create(user=user)


def _email_brand_context():
    """Contexte commun pour les emails HTML (couleurs P&B + CID logo)."""
    has_logo = _logo_path().is_file()
    return {
        'site_name': 'P&BENTREPRISE',
        'site_tagline': 'P&B Entreprise',
        'has_logo': has_logo,
        'logo_src': f'cid:{LOGO_CID}' if has_logo else '',
        'color_primary': '#a83232',
        'color_secondary': '#e8b4b4',
        'color_text': '#1a1a1a',
        'color_heading': '#1a1a1a',
        'color_muted': '#5c5c5c',
        'color_bg': '#fbf5f5',
        'color_card': '#ffffff',
        'color_accent_bg': '#fbeded',
        'login_url': _login_url(),
    }


def _build_related_mime_message(*, subject, recipient, text_body, html_body):
    """
    Message multipart/related (HTML + logo inline).
    Compatible Gmail — contrairement aux data: URI ou localhost.
    """
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or settings.EMAIL_HOST_USER

    root = MIMEMultipart('related')
    root['Subject'] = subject
    root['From'] = from_email
    root['To'] = recipient

    alternative = MIMEMultipart('alternative')
    root.attach(alternative)
    alternative.attach(MIMEText(text_body, 'plain', 'utf-8'))
    alternative.attach(MIMEText(html_body, 'html', 'utf-8'))

    logo_path = _logo_path()
    if logo_path.is_file():
        with logo_path.open('rb') as logo_file:
            image = MIMEImage(logo_file.read(), _subtype='png')
        image.add_header('Content-ID', f'<{LOGO_CID}>')
        image.add_header('Content-Disposition', 'inline', filename='new_logo.png')
        root.attach(image)

    return from_email, root


def _send_branded_email(*, subject, recipient, template_name, context):
    """Envoie un email HTML avec logo inline."""
    full_context = {**_email_brand_context(), **context}
    html_body = render_to_string(template_name, full_context)
    text_body = strip_tags(html_body)

    from_email, mime_message = _build_related_mime_message(
        subject=subject,
        recipient=recipient,
        text_body=text_body,
        html_body=html_body,
    )

    connection = get_connection()
    connection.open()
    try:
        connection.connection.sendmail(from_email, [recipient], mime_message.as_string())
    finally:
        connection.close()


def send_account_created_email(*, user, password, subject):
    """Email envoyé après la création d'un compte utilisateur (mot de passe + lien d'activation)."""
    try:
        token_obj = create_email_verification_token(user)
        _send_branded_email(
            subject=subject,
            recipient=user.email,
            template_name='email/compte_success.html',
            context={
                'user': user,
                'username': user.username,
                'password': password,
                'activation_url': _activation_url(token_obj.token),
            },
        )
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email de création de compte: {e}")
        return False


def send_activation_resend_email(user):
    """Renvoie un email avec un nouveau lien d'activation (verify-email)."""
    try:
        token_obj = create_email_verification_token(user)
        _send_branded_email(
            subject='Activation de compte — P&BENTREPRISE',
            recipient=user.email,
            template_name='email/activation_resend.html',
            context={
                'user': user,
                'username': user.username,
                'activation_url': _activation_url(token_obj.token),
            },
        )
        return True
    except Exception as e:
        logger.error(f"Erreur lors du renvoi du lien d'activation: {e}")
        return False


def send_password_reset_otp_email(user, otp):
    """Envoie un email avec l'OTP pour la réinitialisation de mot de passe."""
    try:
        _send_branded_email(
            subject='Code de réinitialisation de mot de passe — P&BENTREPRISE',
            recipient=user.email,
            template_name='email/pwd_reset_otp.html',
            context={
                'user': user,
                'otp': otp,
                'expires_in': '5 minutes',
            },
        )
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email OTP: {e}")
        return False


def send_email_with_html_body(subjet: str, receivers: list, template: str, context: dict):
    """Compatibilité ascendante — délègue au système d'emails brandés."""
    if not receivers:
        return False
    recipient = receivers[0]
    template_name = template if template.startswith('email/') else f'email/{Path(template).name}'
    try:
        _send_branded_email(
            subject=subjet,
            recipient=recipient,
            template_name=template_name,
            context=context,
        )
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email: {e}")
        return False


def search_vehicules(queryset, search_query):
    """
    Filtre les véhicules selon l'immatriculation, le numéro de carte grise ou le numéro de châssis
    """
    if search_query:
        queryset = queryset.filter(
            Q(immatriculation__icontains=search_query) |
            Q(num_cart_grise__icontains=search_query) |
            Q(num_Chassis__icontains=search_query) |
            Q(marque__icontains=search_query)
        )
    return queryset
