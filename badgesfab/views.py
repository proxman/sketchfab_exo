from django.shortcuts import render

from .serializers import BadgeSerializer
from rest_framework import filters
from rest_framework import generics
from .models import Badge

class BadgeListView(generics.ListAPIView):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    filter_backends = (filters.DjangoFilterBackend,)

