from tastypie.resources import ModelResource,ALL,ALL_WITH_RELATIONS
from tastypie.authorization import Authorization
from AbroadPassProject.AbroadPassApp.models import Country,City,School,Major
from tastypie import fields

class CountryResource(ModelResource):
    class Meta:
        queryset = Country.objects.all()
        resource_name = 'country'
        authorization = Authorization()
        filtering = {
            'name':ALL
        }

class CityResource(ModelResource):
    country = fields.ForeignKey(CountryResource,'country')
    class Meta:
        queryset = City.objects.all()
        resource_name = 'city'
        authorization = Authorization()
        filtering ={
            'name':ALL,
            'country':ALL_WITH_RELATIONS
        }

class SchoolResource(ModelResource):
    city = fields.ForeignKey(CityResource,'city')
    class Meta:
        queryset = School.objects.all()
        resource_name = 'school'
        authorization = Authorization()
        filtering ={
            'city':ALL_WITH_RELATIONS
        }

class MajorResource(ModelResource):
    class Meta:
        queryset = Major.objects.all()
        resource_name = 'major'