from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from badgesfab.models import Rule
from django.contrib.contenttypes.models import ContentType
from .admin import RuleForm


class RuleTestCase(TestCase):

    def setUp(self):
        limited_ctypes = ContentType.objects.filter(Rule.limit)
        self.rule1 = Rule.objects.create(name='Collector', content_type=limited_ctypes[0])

    def test_name_only_rule(self):
        """ Name only rule will fail """
        self.rule = Rule(name="Star")
        with self.assertRaises(IntegrityError):
            self.rule.save()

    def test_contenttype_limit_rule(self):
        """ save rule with asked limit_choices_to without model field defined"""
        limited_ctypes = ContentType.objects.filter(Rule.limit)
        self.rule = Rule(name="Star", content_type=limited_ctypes[0])
        with self.assertRaises(ValidationError):
            self.rule.full_clean()

    def test_contenttype_out_limit_rule(self):
        """ Off limit selection must fail """
        ctypes = ContentType.objects.all()
        nolimit_ctypes = ContentType.objects.filter(~Rule.limit)
        self.rule = Rule(name="Star", content_type=nolimit_ctypes[0])
        with self.assertRaises(ValidationError):
            self.rule.full_clean()