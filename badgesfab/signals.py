from .models import Rule, RewardRule
from django.contrib.contenttypes.models import ContentType


def modelSaveSignal(sender, **kwargs):
    '''
    Receive model save signal configured in AppConfig of tracked model app.
    This signal receiver needs to be total rewrite and refactored
    :param sender:
    :param kwargs:
    :return:
    '''
    ctype = ContentType.objects.get_for_model(sender)
    all_matching_rules = Rule.objects.filter(content_type=ctype)
    for rule in all_matching_rules:
        model_field = rule.model_field
        operator = rule.operator
        value = rule.value
        instance = kwargs['instance']
        get_method = getattr(instance, model_field)
        if hasattr(get_method, '__call__'):
            field = getattr(instance, model_field)()
        else:
            field = get_method
        if field is None:
            continue
        # Check if rule matching
        op = getattr(field, operator)
        if op(type(field)(value)):
            # Attribute the badge
            matched_reward = RewardRule.objects.get(rule=rule)
            rewarded_type = matched_reward.rewarded_type.model_class()
            award = matched_reward.award
            # Search rewarded type among instance field
            obj = [i for i in instance._meta.get_fields_with_model() if i[0].related_model == rewarded_type]
            if not obj:
                # Search rewarded type among related field
                for i in instance._meta.get_all_related_objects():
                    related_model = i.related_model
                    for j in related_model._meta.get_fields_with_model():
                        if j[0].related_model == rewarded_type:
                            winner = getattr(getattr(instance, i.name), j[0].name)
                            if hasattr(winner, 'badges'):
                                winner.badges.add(award)
            else:
                winner = getattr(instance, obj[0])
                if hasattr(winner, 'badges'):
                    winner.badges.add(award)

