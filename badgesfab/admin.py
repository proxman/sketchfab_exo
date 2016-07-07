from django.contrib import admin
from django import forms
from .models import Badge, BadgedItem, Rule, RewardRule
from .utils import get_contenttype_model_fields, get_contenttype_model_properties
from django.forms.utils import ErrorList
from django.utils.translation import ugettext as _
from .forms import RuleForm


class RuleOptions(admin.ModelAdmin):
    # # define the related_lookup_fields
    # related_lookup_fields = {
    #     'generic': [['content_type']],
    # }
    form = RuleForm

    def get_form(self, request, obj=None, **kwargs):
        # We can't use formfield_for_choice_field here, because choices must be a subset of
        # model choices. If model validation fail and there is no possibility to retrieve the
        # fields of the selected content_type model class.
        response = super(RuleOptions, self).get_form(request, obj, **kwargs)
        response.base_fields['model_field'].choices = get_contenttype_model_fields(self, request) +\
                                                      get_contenttype_model_properties(self, request)

        return response

    # def save_form(self, request, form, change):
    #     instances = form.save(commit=True)
    #     return super().save_form(request, form, change)

    def save_model(self, request, obj, form, change):
        fields = ['model_field', 'operator', 'value']
        for field in fields:
            if field in request.POST:
                if hasattr(obj, field):
                    setattr(obj, field, request.POST.get(field))
                    obj.save()
        super(RuleOptions, self).save_model(request, obj, form, change)


class BadgedItemInline(admin.StackedInline):
    model = BadgedItem


class TagAdmin(admin.ModelAdmin):
    inlines = [BadgedItemInline]
    list_display = ["name", "slug"]
    ordering = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}


admin.site.register(Badge, TagAdmin)
admin.site.register(Rule, RuleOptions)
admin.site.register(RewardRule)
