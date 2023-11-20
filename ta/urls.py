"""
URL configuration for ta project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.cache import cache_page
from rest_framework import routers
from turnover_atlas.viewsets import TurnoverAtlasDataViewSets, TurnoverAtlasDataValueViewSets, AccessionIDMapViewSets, \
    SampleGroupMetadataViewSets, ModelParametersViewSets, ProteinSequenceViewSets
from turnover_atlas.views import AvailableTissues, ModelData

router = routers.DefaultRouter()
from rest_framework.authtoken import views

router.register(r'api/turnoverdata', TurnoverAtlasDataViewSets)
router.register(r'api/turnoverdatavalue', TurnoverAtlasDataValueViewSets)
router.register(r'api/accessionmap', AccessionIDMapViewSets)
router.register(r'api/samplegroupmetadata', SampleGroupMetadataViewSets)
router.register(r'api/modelparameters', ModelParametersViewSets)
router.register(r'api/proteinsequence', ProteinSequenceViewSets)
urlpatterns = [
    path('', include(router.urls)),
    path('api/tissue/', AvailableTissues.as_view(), name='tissue'),
    path('api/modelling/', ModelData.as_view(), name='modelling'),
    path('admin/', admin.site.urls),
    path('api-token-auth/', views.obtain_auth_token)
]
