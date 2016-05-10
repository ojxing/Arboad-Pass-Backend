"""AbroadPassProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from tastypie.api import Api
from AbroadPassApp.api import NormalUserResource,UserResource,ProviderResource,NotificationResource,ArticleResource,ApplicationResource
from AbroadPassApp.myapi.StaticResource import CountryResource,CityResource,SchoolResource,MajorResource
v1_api = Api(api_name='v1')
v1_api.register(NormalUserResource())
v1_api.register(UserResource())
v1_api.register(ProviderResource())
v1_api.register(NotificationResource())
v1_api.register(ArticleResource())

v1_api.register(CountryResource())
v1_api.register(CityResource())
v1_api.register(SchoolResource())
v1_api.register(MajorResource())

v1_api.register(ApplicationResource())



urlpatterns = [
    url(r'^api/',include(v1_api.urls)),
    url(r'^admin/', admin.site.urls),
]
