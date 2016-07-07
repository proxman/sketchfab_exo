from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from .models import Badge, Rule


class DynamicChoiceField(forms.ChoiceField):

    def validate(self, value):
        # Override form validation because choice are dynamically generate against content_type field
        pass

    def to_python(self, value):
        # TODO: check here if the value is pythonable
        return super().to_python(value)


class RuleForm(forms.ModelForm):
    model_field = DynamicChoiceField()

    class Meta:
        model = Rule
        fields = '__all__'

    def clean_content_type(self):
        clean_data = self.cleaned_data['content_type']
        if clean_data not in ContentType.objects.filter(self._meta.model.limit):
            raise ValidationError('Object to compare need to be a part of %s models' % settings.BADGESFAB_APP_MODELS_LIMIT)
        return clean_data


class BadgeField(forms.ModelMultipleChoiceField):
    widget = FilteredSelectMultiple(verbose_name=_('Badge(s)'), is_stacked=False)

    def __init__(self, queryset, required=True, widget=None, label=None, initial=None, help_text='', *args, **kwargs):
        queryset_badge = Badge.objects.all()
        super(BadgeField, self).__init__(queryset=queryset_badge, required=required, widget=widget, label=label,
                                         initial=initial, help_text=help_text, *args, **kwargs)


# TODO: Inject custom css to show badge image in admin UI
# class BadgeWidget(FilteredSelectMultiple):
#     @property
#     def media(self):
#         # TODO: Finish to render the badge image on UI
#         media = super(BadgeWidget, self).media
#         dynamic_css = os.path.join('css', 'dynamic_css.css')
#         content_css_list = []
#         with open(os.path.join(settings.STATIC_ROOT, dynamic_css), mode='w') as cssfile:
#             for badge in self.choices.queryset.all():
#                 content_css_list.append("background-image:url(" + badge.badge_avatar.url + ");")
#             css_content = '\n'.join(content_css_list)
#             cssfile.write(css_content)
#         css = {
#             "all": (
#                 dynamic_css,
#             )
#         }
#         media.add_css(css)
#         return media