# -*- coding: utf-8 -*-
import requests
from requests.auth import HTTPBasicAuth
import json
#-------------------------------Authentication-------------------------------#

#--------login---------#
login = 'http://localhost:8000/api/v1/user/login/'
data1 = {'username':'ojxing2','password':'abc123'}
head = {'Content-type':'application/json'}
r1 = requests.post(login,json.dumps(data1),headers=head)
apikey = json.loads(r1.content)["api"]
print(r1.status_code)
print(r1.content)
print(r1.cookies['sessionid'])

# article = 'http://localhost:8000/api/v1/article/post/'
# data1 = {'content':'abctest','read':15}
# head = {'Content-type':'application/json'}
# r = requests.post(article,json.dumps(data1),headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
# print(r.status_code)
# print(r.content)
# print(r.cookies)

article = 'http://localhost:8000/api/v1/article/like/?id=2'
data1 = {'content':'abctest','read':15}
head = {'Content-type':'application/json'}
r = requests.post(article,json.dumps(data1),headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
print(r.status_code)
print(r.content)
print(r.cookies)

#---------register---------#
# reg_url = 'http://localhost:8000/api/v1/user/register/'
# head = {'Content-type':'application/json'}
# data = {'username':'ojxing9','password':'abc123','type':'normaluser'}  #type =>  normaluser or provider
# r = requests.post(reg_url,json.dumps(data),headers=head)
# print(r.status_code)
# print(r.content)

#-------logout--------#
# reg_url = 'http://localhost:8000/api/v1/user/logout/'
# head = {'Content-type':'application/json'}
# #data = {'username':u'家兴','password':'newpass'}
# r = requests.get(reg_url,headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
# print(r.status_code)
# print(r.content)
# print(r.cookies)

#-----changepassword-----#
# login = 'http://localhost:8000/api/v1/user/changepassword/'
# data1 = {'oldpassword':'newpass','newpassword':'ojx9103123'}
# head = {'Content-type':'application/json'}
# r = requests.post(login,json.dumps(data1),headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
# print(r.status_code)
# print(r.content)
# print(r.cookies)

#-------------------------------Profile Management-------------------------------#

#-------provider list------#
# provider_list = 'http://localhost:8000/api/v1/provider/'
# head = {'Content-type':'application/json'}
# r = requests.get(provider_list,headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
# print(r.status_code)
# print(json.dumps(json.loads(r.content),indent=1))
# print(r.cookies)

#-------provider profile------#
# provider_profile = 'http://localhost:8000/api/v1/provider/show/'
# head = {'Content-type':'application/json'}
# r = requests.get(provider_profile,headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
# print(r.status_code)
# print(json.dumps(json.loads(r.content),indent=1))
# print(r.cookies)

#------update provider profile-----#
# update_provider = 'http://localhost:8000/api/v1/provider/edit/'
# data1 = {'nationality':'china','mobile':'123456789','email':'mrojxing@163.com','user_realname':'区家兴'}
# head = {'Content-type':'application/json','X-CSRFToken':r1.cookies['csrftoken']}
# r = requests.put(update_provider,json.dumps(data1),headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
# print(r.status_code)
# print(r.content)
# print(r)

#---------normal user list---------#
# normaluser_list = 'http://localhost:8000/api/v1/normaluser/'
# head = {'Content-type':'application/json'}
# r = requests.get(normaluser_list,headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
# print(r.status_code)
# print(json.dumps(json.loads(r.content),indent=1))
# print(r.cookies)

#---------normal user profile---------#
# normaluser_profile = 'http://localhost:8000/api/v1/normaluser/show/'
# head = {'Content-type':'application/json'}
# r = requests.get(normaluser_profile,headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
# print(r.status_code)
# print(json.dumps(json.loads(r.content),indent=1))
# print(r.cookies)

#--------update normal user profile----------#
# update_provider = 'http://localhost:8000/api/v1/normaluser/edit/'
# data1 = {'nationality':'hk','mobile':'18588766631','email':'mrojxing@163.com'}
# head = {'Content-type':'application/json','X-CSRFToken':r1.cookies['csrftoken']}
# r = requests.put(update_provider,json.dumps(data1),headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
# print(r.status_code)
# print(r.content)
# print(r)


#-------------------------------School List Management-------------------------------#

#-------country list------#
# country_list = 'http://localhost:8000/api/v1/country/'
# head = {'Content-type':'application/json'}
# r = requests.get(country_list,headers=head)
# print(r.status_code)
# print(json.dumps(json.loads(r.content),indent=1,ensure_ascii=False))
# print(r.cookies)

#-------city list------#
# city_list = 'http://localhost:8000/api/v1/city/?country__name=美国'
# head = {'Content-type':'application/json'}
# r = requests.get(city_list,headers=head)
# print(r.status_code)
# print(json.dumps(json.loads(r.content),indent=1,ensure_ascii=False))
# print(r.cookies)

#-------school list------#
# school_list = 'http://localhost:8000/api/v1/school/?city__name=北京'
# head = {'Content-type':'application/json'}
# r = requests.get(school_list,headers=head)
# print(r.status_code)
# print(json.dumps(json.loads(r.content),indent=1,ensure_ascii=False))
# print(r.cookies)

#-------major list------#
# major_list = 'http://localhost:8000/api/v1/major/'
# head = {'Content-type':'application/json'}
# r = requests.get(major_list,headers=head)
# print(r.status_code)
# print(json.dumps(json.loads(r.content),indent=1,ensure_ascii=False))
# print(r.cookies)

#-------notification list------#
# major_list = 'http://localhost:8000/api/v1/notification/'
# head = {'Content-type':'application/json'}
# r = requests.get(major_list,headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
# print(r.status_code)
# print(json.dumps(json.loads(r.content),indent=1,ensure_ascii=False))
# print(r.cookies)


#-------------------------------Trainee Management （商家）-------------------------------#
#-------Add Trainee------#
# trainee_url = 'http://localhost:8000/api/v1/trainee/'
# head = {'Content-type':'application/json'}
# data = {'name':'eastern','sub_title':'abc123','mobile':18588766631}  #type =>  normaluser or provider
# r = requests.post(trainee_url,json.dumps(data),headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
# print(r.status_code)
# print(r.content)

#-------Trainee List------#
