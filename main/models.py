from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _


class Module(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=128)
    author = models.CharField(verbose_name=_("Author"), max_length=512, null=True, blank=True)
    author_email = models.CharField(verbose_name=_("Author email"), max_length=512, null=True, blank=True)
    home_page = models.CharField(verbose_name=_("Home page"), max_length=1024, null=True, blank=True)
    description = models.TextField(verbose_name=_('Description'), max_length=4000, blank=True, null=True)
    version = models.PositiveIntegerField(verbose_name=_("Version"), default=1)
    in_menu = models.BooleanField(verbose_name=_("In Menu"), default=True)
    is_enabled = models.BooleanField(verbose_name=_("Enabled"), default=True)
    is_removed = models.BooleanField(verbose_name=_("Removed"), default=False)
    installed_at = models.DateTimeField(verbose_name=_("Date of Creation"), auto_now_add=True)
    update_at = models.DateTimeField(verbose_name=_("Date of Update"), auto_now=True)

    class Meta:
        verbose_name_plural = _('Modules')
        verbose_name = _('Module')

    def __unicode__(self):
        return self.name


class Log(models.Model):
    ACTIONS = (
        (0, _('Module add')),
        (1, _('Module update')),
        (2, _('Module upgrade')),
        (3, _('Module remove')),
    )

    date = models.DateTimeField(verbose_name=_("Date and time"), auto_now_add=True)
    action = models.PositiveSmallIntegerField(verbose_name=_("Action"), choices=ACTIONS)
    user = models.ForeignKey(User, verbose_name=_("User"), null=True, blank=True)

    class Meta:
        verbose_name_plural = _('Logs')
        verbose_name = _('Log')
        ordering = ['-date']

    def __unicode__(self):
        return u"%s: %s" % (self.date, self.get_action_display())