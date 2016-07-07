from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.conf import settings
from itertools import chain

EMPTY = [(None, _('Select object to compare then "Save and continue" to load object\'s fields'))]


def get_modelclass(modeladmin, request):
    '''
    Return the model class of the passed content_type. Return None when not able to retrieve it.
    :param modeladmin:
    :param request:
    :return:
    '''
    if '_continue' in request.POST:
        content_type_id = request.POST.get('content_type', False)
        if not content_type_id or content_type_id == '':
            return None
        content_type = ContentType.objects.get_for_id(content_type_id)
        modelclass = content_type.model_class()
        return modelclass
    elif len(request.resolver_match.args) > 0:
        # Get ID of resolved Rule URL
        rule_instance = modeladmin.model.objects.get(pk=request.resolver_match.args[0])
        # Get contenttype model class of this rule
        modelclass = rule_instance.content_type.model_class()
        return modelclass

    return None


def get_contenttype_model_properties(modeladmin, request, filter_method=('_count',)):
    '''
    Retreive model class method for a content type to compare with.
    :param modeladmin: ModelAdmin instance
    :param request: Request instance
    :param filter_method: Tuple with end of property string to add to Rule Model fields list.
    :return:
    '''
    filter_method += settings.BADGESFAB_PROPERTIES
    modelclass = get_modelclass(modeladmin, request)

    if modelclass is not None:
        property_names = [f for f in dir(modelclass) if not f.startswith('_') and f.endswith(filter_method)]
        return [(p, p) for p in property_names]
    else:
        return EMPTY


def get_contenttype_model_fields(modeladmin, request):
    '''
    Retreive model class fields for a content type to compare with.
    :param modeladmin:
    :param request:
    :return:
    '''
    modelclass = get_modelclass(modeladmin, request)
    if modelclass is None:
        return EMPTY

    field_names = [f for f in modelclass._meta.get_all_field_names() if not f.endswith('_id')]
    choices = [(None, '---------')]
    for field_name in field_names:
        field = modelclass._meta.get_field_by_name(field_name)
        field_name_path = dict()
        if not field[2]:
            field_name_path[field_name] = list()
            related_object = field[0]
            related_model = related_object.related_model
            for related_field_name in related_model._meta.get_all_field_names():
                rel_field = related_model._meta.get_field_by_name(related_field_name)[0]
                if hasattr(rel_field, 'verbose_name'):
                    field_name_path[field_name].append(rel_field.name)
            # Append field with related model field
            for f in field_name_path[field_name]:
                choices.append(('{}.{}'.format(field_name, f), '{}.{}'.format(field_name, f)))
        else:
            # str force evaluation of lazy field [1]
            # https://docs.djangoproject.com/en/dev/ref/models/querysets/#when-querysets-are-evaluated
            if hasattr(field[0], 'verbose_name'):
                choices.append((field_name, str(field[0].verbose_name)))
    return choices


def get_fields_with_model(instance):
    return [
        (f, f.model if f.model != instance else None)
        for f in instance._meta.get_fields()
        if not f.is_relation
        or f.one_to_one
        or (f.many_to_one and f.related_model)
        ]


def get_concrete_fields_with_model(instance):
    return [
        (f, f.model if f.model != instance else None)
        for f in instance._meta.get_fields()
        if f.concrete and (
            not f.is_relation
            or f.one_to_one
            or (f.many_to_one and f.related_model)
        )
        ]


def get_m2m_with_model(instance):
    return [
        (f, f.model if f.model != instance else None)
        for f in instance._meta.get_fields()
        if f.many_to_many and not f.auto_created
        ]


def get_all_related_objects(instance):
    return [
        f for f in instance._meta.get_fields()
        if (f.one_to_many or f.one_to_one) and f.auto_created
        ]


def get_all_related_objects_with_model(instance):
    return [
        (f, f.model if f.model != instance else None)
        for f in instance._meta.get_fields()
        if (f.one_to_many or f.one_to_one) and f.auto_created
        ]


def get_all_related_many_to_many_objects(instance):
    return [
        f for f in instance._meta.get_fields(include_hidden=True)
        if f.many_to_many and f.auto_created
        ]


def get_all_related_m2m_objects_with_model(instance):
    return [
        (f, f.model if f.model != instance else None)
        for f in instance._meta.get_fields(include_hidden=True)
        if f.many_to_many and f.auto_created
        ]


def get_all_field_names(instance):
    return list(set(chain.from_iterable(
        (field.name, field.attname) if hasattr(field, 'attname') else (field.name,)
        for field in instance._meta.get_fields()
        # For complete backwards compatibility, you may want to exclude
        # GenericForeignKey from the results.
        if not (field.many_to_one and field.related_model is None)
    )))
