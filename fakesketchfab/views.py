from django.shortcuts import render

from django.conf import settings
from fakesketchfab.models import SketchFabUser
from fakesketchfab.models import Model3d
from django.views.generic import ListView, DetailView

from fakesketchfab.serializers import UserSerializer
from rest_framework import filters
from rest_framework import generics

from django.http import HttpResponse
from actstream.models import model_stream
from django.apps import AppConfig

def index(request):
    skuser = SketchFabUser.objects.get(user=request.user)
    #test = model_stream(skuser, with_user_activity=True)
    return HttpResponse("Hello, world. You're at the polls index.")


class FakeModel3DViewList(ListView):
    model = Model3d


class FakeModel3DDetailView(DetailView):
    model = Model3d

    def get(self, request, *args, **kwargs):
        if not request.session.get('already_view', False) or settings.DEBUG:
            model3d = self.model.objects.get()
            model3d.about.users_views_count += 1
            request.session['already_view'] = True
            model3d.about.save()
        return super().get(request, *args, **kwargs)


class UserListView(generics.ListAPIView):
    queryset = SketchFabUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
