from tastypie.resources import ModelResource,ALL,ALL_WITH_RELATIONS
from tastypie.authorization import Authorization
from AbroadPassProject.AbroadPassApp.models import Trainee,Course
from AbroadPassProject.AbroadPassApp.api import UserResource
from tastypie import fields

class TraineeResource(ModelResource):
    user = fields.ForeignKey(UserResource,'user')
    def hydrate(self, bundle):
        bundle.obj.user = bundle.request.user
        return bundle
    class Meta:
        queryset = Trainee.objects.all()
        resource_name = 'trainee'
        authorization = Authorization()
        filtering = {
            'name':ALL,
            'category':ALL,
            'sub_category':ALL
        }

class CourseResource(ModelResource):
    trainee = fields.ForeignKey(TraineeResource,'trainee')
    class Meta:
        queryset = Course.objects.all()
        resource_name = 'course'
        authorization = Authorization()
        filtering ={
            'name':ALL,
            'trainee':ALL_WITH_RELATIONS,
            'category':ALL,
            'sub_category':ALL
        }