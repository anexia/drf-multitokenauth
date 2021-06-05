import binascii
import os

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

__all__ = [
    'MultiToken',
]

# Prior to Django 1.5, the AUTH_USER_MODEL setting does not exist.
# Note that we don't perform this code in the compat module due to
# bug report #1297
# See: https://github.com/tomchristie/django-rest-framework/issues/1297
AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class MultiToken(models.Model):
    """
    The multi token model with user agent and IP address.
    """

    id = models.AutoField(
        primary_key=True
    )

    key = models.CharField(
        _("Key"),
        max_length=64,
        db_index=True,
        unique=True
    )
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name='auth_tokens',
        on_delete=models.CASCADE,
        verbose_name=_("User")
    )
    created = models.DateTimeField(
        _("Created"),
        auto_now_add=True
    )
    last_known_ip = models.GenericIPAddressField(
        _("The IP address of this session"),
        default="127.0.0.1"
    )
    user_agent = models.CharField(
        max_length=256,
        verbose_name=_("HTTP User Agent"),
        default=""
    )

    class Meta:
        # Work around for a bug in Django:
        # https://code.djangoproject.com/ticket/19422
        #
        # Also see corresponding ticket:
        # https://github.com/tomchristie/django-rest-framework/issues/705
        abstract = 'django_rest_multitokenauth' not in settings.INSTALLED_APPS
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(MultiToken, self).save(*args, **kwargs)

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        return binascii.hexlify(os.urandom(32)).decode()

    def __str__(self):
        return "{} (user {} with IP {} and user-agent {})".format(
            self.key, self.user, self.last_known_ip, self.user_agent
        )
