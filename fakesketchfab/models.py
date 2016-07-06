import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField
from taggit.managers import TaggableManager
from badgesfab.managers import BadgeManager
from django.utils import timezone


class DummyModel(models.Model):
    pass


class SketchFabUser(models.Model):
    """
    Extend :model:`User` model, which it related to.
    :model:`ModelDescription` which store metadata about an upload and to.
    It's also related to :model:`DummyModel` which represent a model storing all social networks links.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255, verbose_name=_('Display name'), name='display_name')
    tagline = models.SlugField(verbose_name=_('Your Tagline'))
    account_type = models.CharField(max_length=128, default='Field not implemented yet')
    avatar = models.CharField(max_length=128, default='Field not implemented yet')
    bio = models.CharField(max_length=128, default='Field not implemented yet')
    location = models.CharField(max_length=128, default='Field not implemented yet')
    badges = BadgeManager(related_name='badgestag', blank=True)
    socials = DummyModel()
    skills = TaggableManager(blank=True)

    # TODO: this method must be handle in Badgesfab model
    def account_age(self):
        if self._state.adding:
            return timezone.now() - self.user.created_at
        else:
            return 0
    account_age.verbose_name = 'User\'s account old'

    def __str__(self):
        return "%s" % self.display_name

    class Meta:
        verbose_name = _('SketchFab User')
        verbose_name_plural = _('SketchFab Users')
        app_label = 'fakesketchfab'


class Model3d(models.Model):
    """
    Store 3d object uploaded by Users, related to :model:`ModelDescription` which store metadata about an upload and to
     :model:`SketchFabUser`

    """
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    filename = models.FileField(verbose_name=_('Model file to upload'), name='filename')
    uploader = models.ForeignKey(
        SketchFabUser,
        models.SET_NULL,
        blank=True, null=True,
    )
    about = models.OneToOneField('ModelDescription',
                                 related_name='model_3d',
                                 blank=True,
                                 null=models.SET_NULL,
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('3D Model')
        verbose_name_plural = _('3D Models')


class ModelDescription(models.Model):
    """
    Store metadata about 3d object uploaded by Users.
    """
    LICENSE_CC = (
        ('BY', _('Attribution')),
        ('NC', _('Noncommercial')),
        ('ND', _('No Derivative Works')),
        ('SA', _('Large')),
    )
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=5000, verbose_name=_('About this model'))
    published_at = models.DateTimeField(blank=True, null=models.SET_NULL)
    published = models.BooleanField(default=False)
    users_views_count = models.PositiveIntegerField(verbose_name=_('Views'), default=0)
    labels = TaggableManager(blank=True)
    allow_download = models.BooleanField(verbose_name=_('Share this model'), default=False)
    price = MoneyField(max_digits=10, decimal_places=0, default_currency=settings.DEFAULT_CURRENCY, default=0)
    license = models.CharField(max_length=2, choices=LICENSE_CC, blank=True, null=models.SET_NULL)
    categories = models.CharField(max_length=128, default='Field not implemented yet')
    private_model = models.CharField(max_length=128, default='Field not implemented yet')

    # TODO: this method must be handle in Badgesfab model
    def models_per_uploader_count(self):
        uploader = self.model_3d.uploader
        return Model3d.objects.filter(uploader=uploader).count()
    models_per_uploader_count.verbose_name = 'User\'s model count'

    # def __str__(self):
    #     return self.name

    class Meta:
        verbose_name = _('Model\'s About')
        verbose_name_plural = _('Models About')

