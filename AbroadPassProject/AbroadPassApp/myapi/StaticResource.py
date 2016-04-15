from tastypie.resources import ModelResource,ALL,ALL_WITH_RELATIONS
from tastypie.authorization import Authorization
from AbroadPassProject.AbroadPassApp.models import Country,City,School,Major
from AbroadPassProject.AbroadPassApp.api import MyModelResource
from tastypie.http import HttpUnauthorized,HttpForbidden,HttpNotFound,HttpAccepted
from tastypie import fields

def build_content_type(format, encoding='utf-8'):
    """
    Appends character encoding to the provided format if not already present.
    """
    if 'charset' in format:
        return format

    return "%s; charset=%s" % (format, encoding)

class CountryResource(MyModelResource):
    class Meta:
        queryset = Country.objects.all()
        resource_name = 'country'
        authorization = Authorization()
        filtering = {
            'name':ALL
        }
    def create_response(self, request, data, response_class=HttpAccepted, **response_kwargs):
        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        response = response_class(content=serialized, content_type=build_content_type(desired_format), **response_kwargs)
        response['Access-Control-Allow-Origin'] = '*'
        return response

class CityResource(MyModelResource):
    country = fields.ForeignKey(CountryResource,'country')
    class Meta:
        queryset = City.objects.all()
        resource_name = 'city'
        authorization = Authorization()
        filtering ={
            'name':ALL,
            'country':ALL_WITH_RELATIONS
        }

class SchoolResource(MyModelResource):
    city = fields.ForeignKey(CityResource,'city')
    class Meta:
        queryset = School.objects.all()
        resource_name = 'school'
        authorization = Authorization()
        filtering ={
            'city':ALL_WITH_RELATIONS
        }

class MajorResource(MyModelResource):
    class Meta:
        queryset = Major.objects.all()
        resource_name = 'major'