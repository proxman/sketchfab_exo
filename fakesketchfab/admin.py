from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django import forms


# Register your models here.
from .models import SketchFabUser, Model3d, ModelDescription


class SkfUserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.display_name


class Model3dAdminForm(forms.ModelForm):
    uploader = SkfUserChoiceField(queryset=SketchFabUser.objects.all())

    class Meta:
        model = Model3d
        fields = ['filename']
        exclude = ['about_id']


class Model3DInline(admin.StackedInline):
    model = Model3d
    form = Model3dAdminForm
    can_delete = False
    verbose_name_plural = 'Models'


class ModelDescriptionAdmin(admin.ModelAdmin):
    inlines = (Model3DInline,)


# class Model3DInline(admin.StackedInline):
#     model = Model3d
#     form = Model3dAdminForm
#     can_delete = False
#     verbose_name_plural = 'Models'
#
#
# class ModelDescriptionAdmin(admin.ModelAdmin):
#     inlines = (Model3DInline,)


# Define an inline admin descriptor for SketchFabUser model
# which acts a bit like a singleton
class SketchFabUserInline(admin.StackedInline):
    model = SketchFabUser
    can_delete = False
    verbose_name_plural = 'Sketchfabusers'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (SketchFabUserInline, )
    search_fields = ('display_name',)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(SketchFabUser)
admin.site.register(ModelDescription, ModelDescriptionAdmin)