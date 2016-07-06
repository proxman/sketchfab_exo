from badgesfab.models import Badge
from rest_framework import serializers
from fakesketchfab.models import SketchFabUser


class UserSerializer(serializers.ModelSerializer):
    badges = serializers.PrimaryKeyRelatedField(many=True, queryset=Badge.objects.all())

    class Meta:
        model = SketchFabUser
        fields = ('id', 'display_name', 'badges')


class BadgeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Badge
        fields = ('id', 'badge_avatar')