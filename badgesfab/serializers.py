from badgesfab.models import Badge
from rest_framework import serializers


class BadgeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Badge
        fields = ('id', 'badge_avatar')