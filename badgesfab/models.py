from __future__ import unicode_literals

import django
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.db import IntegrityError, models, transaction
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _
from taggit.models import TagBase, ItemBase

# from django.core.files.storage import FileSystemStorage


# if not hasattr(settings, 'BADGEFAB_FILESYSTEM'):
#     # This can be a security issue !
#     upload_storage = FileSystemStorage(location=settings.BADGEFAB_STATIC_ROOT, base_url='/badges')
# else:
#     upload_storage = settings.BADGEFAB_FILESYSTEM

try:
    from unidecode import unidecode
except ImportError:
    def unidecode(tag):
        return tag

try:
    from django.contrib.contenttypes.fields import GenericForeignKey
except ImportError:  # django < 1.7
    from django.contrib.contenttypes.generic import GenericForeignKey

try:
    atomic = transaction.atomic
except AttributeError:
    from contextlib import contextmanager


    @contextmanager
    def atomic(using=None):
        sid = transaction.savepoint(using=using)
        try:
            yield
        except IntegrityError:
            transaction.savepoint_rollback(sid, using=using)
            raise
        else:
            transaction.savepoint_commit(sid, using=using)


class Rule(models.Model):
    COMP_OP = (
        ('__eq__', '=='),
        ('__ne__', '!='),
        ('__lt__', '<'),
        ('__gt__', '>'),
        ('__le__', '<='),
        ('__ge__', '>='),
    )

    LOGICAL_OP = (
        ('__and__', '&&'),
        ('__or__', '!='),
    )

    class Meta:
        app_label = 'badgesfab'

    name = models.CharField(max_length=30, verbose_name=_('Rule\'s name'))
    limit = models.Q(app_label=settings.BADGESFAB_APP_MODELS_LIMIT)

    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     null=False,
                                     limit_choices_to=limit,
                                     blank=False,
                                     related_name="content_type",
                                     verbose_name='Object to compare with')

    model_field = models.CharField(max_length=30, blank=True, null=models.SET_NULL)

    operator = models.CharField(max_length=6, choices=COMP_OP, blank=True)
    value = models.CharField(max_length=30, blank=True, null=models.SET_NULL, verbose_name=_('Value to compare with'))

    def clean_fields(self, exclude=None):

        return super(Rule, self).clean_fields(exclude)

    def clean(self):
        # Check if instance has content_type
        if not hasattr(self, 'content_type'):
            raise ValidationError({'content_type': _('"Object to compare" must be selected.')}, code='required')

        # Check if selected content_type is limited to configured limit_choices_to
        if self.content_type not in ContentType.objects.filter(self.limit):
            raise ValidationError({'content_type': '"Object to compare" need to be a part of {} models.'.format(
                settings.BADGESFAB_APP_MODELS_LIMIT)}, code='invalid')

        # Get class model for the selected content_type
        modelclass = self.content_type.model_class()

        # Check if a model field is selected
        if isinstance(self.content_type, ContentType) and self.model_field is None or self.model_field == '':
            raise ValidationError({'model_field': _('Model object field or "property" must be selected.')},
                                  code='required')

        # Check if field is really a selected model field.
        if not hasattr(modelclass, self.model_field) and not (
                    self.model_field in modelclass._meta.get_all_field_names()):
            raise ValidationError(
                _('No field named %(model_field)s for %(model)s.'),
                params={'model_field': self.model_field, 'model': modelclass._meta.verbose_name},
            )
        elif not hasattr(self, 'operator'):
            raise ValidationError(_('Operator is required.'))
        elif not hasattr(self, 'value'):
            raise ValidationError(_('Value is required.'))

        # Provoke validation error on the field to check if value type is compliant with selected model field.
        try:
            field = modelclass._meta.get_field(self.model_field)
            field.to_python(self.value)
        except FieldDoesNotExist as e:
            if not hasattr(modelclass, self.model_field):
                raise ValidationError(
                    _('No property named %(model_field)s for %(model)s'),
                    params={'model_field': self.model_field, 'model': modelclass._meta.verbose_name},
                )

        super().clean()

    def __str__(self):
        modelclass = self.content_type.model_class()
        op = dict(self.COMP_OP)
        try:
            model_field_verbose_name = modelclass._meta.get_field_by_name(self.model_field)[0].verbose_name
        except FieldDoesNotExist as e:
            model_field_verbose_name = getattr(modelclass, self.model_field).verbose_name
        return "\"{model}\" - \"{model_field}\" {compare_sign} {value}".format(model_field=model_field_verbose_name,
                                                                               model=self.content_type,
                                                                               compare_sign=op[self.operator],
                                                                               value=self.value)

    class Meta:
        unique_together = ['content_type', 'model_field', 'operator', 'value']


class RewardRule(models.Model):
    rule = models.ForeignKey(Rule,
                             blank=True,
                             null=models.SET_NULL,
                             related_name='reward_rules',
                             related_query_name='reward_rule')
    limit = models.Q(app_label=settings.BADGESFAB_APP_MODELS_LIMIT)
    rewarded_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=models.SET_NULL, limit_choices_to=limit,
        blank=True,
        related_name="rewarded_type",
        verbose_name='Object reward')
    award = models.ForeignKey('Badge', blank=True, null=models.SET_NULL)

    def __str__(self):
        rule_display_str = str(self.rule)
        rewarded_modelclass = self.rewarded_type.model_class()
        badge = self.award.name

        return "\"{rewarded_modelclass}\" will win a \"{badge} badge\" if {rule_display_str} match".format(
            rewarded_modelclass=rewarded_modelclass._meta.verbose_name,
            badge=badge,
            rule_display_str=rule_display_str,
            )


class BadgeItemBase(ItemBase):
    def __str__(self):
        return _("%(object)s received a %(tag)s badge") % {
            "object": self.content_object,
            "tag": self.tag
        }

    class Meta:
        abstract = True


class CommonGenericBadgedItemBase(BadgeItemBase):
    '''
    CommonGenericBadgedItemBase is a copy of CommonGenericTaggedItemBase.
    We need to inherit from ItemBase because python inheritance from CommonGenericTaggedItemBase will
    hide content_type field.
    Seems that Python doesn't allow Field hiding. [1] which forbid us to override related_name parameter to create
    our own badged_item contenttype.
    [1] http://stackoverflow.com/questions/2344751/in-django-model-inheritance-does-it-allow-you-to-override-a-parent-models-a
    '''

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_('Content type'),
        related_name="%(app_label)s_%(class)s_badged_items"
    )
    content_object = GenericForeignKey()

    class Meta:
        abstract = True

    @classmethod
    def lookup_kwargs(cls, instance):
        return {
            'object_id': instance.pk,
            'content_type': ContentType.objects.get_for_model(instance)
        }

    @classmethod
    def bulk_lookup_kwargs(cls, instances):
        if isinstance(instances, QuerySet):
            # Can do a real object_id IN (SELECT ..) query.
            return {
                "object_id__in": instances,
                "content_type": ContentType.objects.get_for_model(instances.model),
            }
        else:
            # TODO: instances[0], can we assume there are instances.
            return {
                "object_id__in": [instance.pk for instance in instances],
                "content_type": ContentType.objects.get_for_model(instances[0]),
            }

    @classmethod
    def tags_for(cls, model, instance=None, **extra_filters):
        ct = ContentType.objects.get_for_model(model)
        kwargs = {
            "%s__content_type" % cls.tag_relname(): ct
        }
        if instance is not None:
            kwargs["%s__object_id" % cls.tag_relname()] = instance.pk
        if extra_filters:
            kwargs.update(extra_filters)
        return cls.tag_model().objects.filter(**kwargs).distinct()


class GenericBadgedItemBase(CommonGenericBadgedItemBase):
    object_id = models.IntegerField(verbose_name=_('Object id'), db_index=True)

    class Meta:
        abstract = True


class Badge(TagBase):
    """
    Override TagBase to define our Badge Model
    """
    badge_avatar = models.ImageField(verbose_name=_("Badge's image"), blank=True, null=True)

    class Meta:
        verbose_name = _("Badge")
        verbose_name_plural = _("Badges")

        # ... methods (if any) here


class BadgedItemBase(ItemBase):
    tag = models.ForeignKey(Badge, related_name="%(app_label)s_%(class)s_items", on_delete=models.CASCADE)

    class Meta:
        abstract = True

    @classmethod
    def tags_for(cls, model, instance=None, **extra_filters):
        kwargs = extra_filters or {}
        if instance is not None:
            kwargs.update({
                '%s__content_object' % cls.tag_relname(): instance
            })
            return cls.tag_model().objects.filter(**kwargs)
        kwargs.update({
            '%s__content_object__isnull' % cls.tag_relname(): False
        })
        return cls.tag_model().objects.filter(**kwargs).distinct()


class BadgedItem(GenericBadgedItemBase, BadgedItemBase):
    class Meta:
        verbose_name = _("Badged Item")
        verbose_name_plural = _("Badged Items")
        app_label = 'badgesfab'
        if django.VERSION >= (1, 5):
            index_together = [
                ["content_type", "object_id"],
            ]


# Ensure that there will be no "collision" if another TaggableManagers is set to the model.
class BagdeThrough(BadgedItemBase):
    content_object = models.ForeignKey(Badge,
                                       on_delete=models.CASCADE)  # TODO: Where to remove on_delete CASCADE to avoid deletion of User


class GenericBadgeManager(GenericBadgedItemBase):
    # TaggedWhatever can also extend TaggedItemBase or a combination of
    # both TaggedItemBase and GenericTaggedItemBase. GenericTaggedItemBase
    # allows using the same tag for different kinds of objects, in this
    # example Food and Drink.

    # Here is where you provide your custom Tag class.
    tag = models.ForeignKey(Badge, related_name="%(app_label)s_%(class)s_items")
