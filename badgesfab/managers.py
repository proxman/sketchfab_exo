from datetime import datetime
from actstream.managers import ActionManager, stream
from taggit.managers import _TaggableManager, TaggableManager
from .models import BagdeThrough, Badge, BadgedItem
from django.utils.translation import ugettext_lazy as _
from badgesfab.forms import BadgeField
from django.utils.text import capfirst


class BadgeActionManager(ActionManager):

    @stream
    def users_model_views_stream(self, obj, verb='reached', time=None):
        if time is None:
            time = datetime.now()
        return obj.actor_actions.filter(verb=verb, timestamp__lte=time)


class _BadgeManager(_TaggableManager):
    def __init__(self, through=BagdeThrough, model=Badge, instance=None, prefetch_cache_name=None):
        super(_BadgeManager, self).__init__(through=through, model=model, instance=instance,
                                            prefetch_cache_name=prefetch_cache_name)


class BadgeManager(TaggableManager):
    def __init__(self, verbose_name=_("Badges"),
                 help_text=_("List of Badges won by this user."),
                 through=None, blank=False, related_name=None, to=None,
                 manager=_BadgeManager):
        self.through = through or BadgedItem

        super(BadgeManager, self).__init__(verbose_name=verbose_name, help_text=help_text, through=self.through,
                                           blank=blank, related_name=related_name, to=to, manager=manager)

    def formfield(self, form_class=BadgeField, **kwargs):
        defaults = {
            "label": capfirst(self.verbose_name),
            "help_text": self.help_text,
            "required": not self.blank,
            "queryset": Badge.objects.none()
        }
        defaults.update(kwargs)
        return form_class(**defaults)