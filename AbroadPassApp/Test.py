# -*- coding: utf-8 -*-
import requests
from requests.auth import HTTPBasicAuth
import json
#-------------------------------Authentication-------------------------------#

#--------login---------#
login = 'http://localhost:8000/api/v1/user/login/'
data1 = {'username':'ojxing5','password':'abc123'}
head = {'Content-type':'application/json'}
r1 = requests.post(login,json.dumps(data1),headers=head)
print(r1.status_code)
print(r1.content)
print(r1.cookies)

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
list = 'http://localhost:8000/api/v1/provider/'
head = {'Content-type':'application/json'}
r = requests.get(list,headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
print(r.status_code)
print(json.dumps(json.loads(r.content),indent=1))
print(r.cookies)

#------update provider profile-----#
# update_provider = 'http://localhost:8000/api/v1/provider/edit/'
# data1 = {'nationality':'hk','mobile':'18588766631','email':'mrojxing@163.com'}
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

#--------update normal user profile----------#
# update_provider = 'http://localhost:8000/api/v1/normaluser/edit/'
# data1 = {'nationality':'hk','mobile':'18588766631','email':'mrojxing@163.com'}
# head = {'Content-type':'application/json','X-CSRFToken':r1.cookies['csrftoken']}
# r = requests.put(update_provider,json.dumps(data1),headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
# print(r.status_code)
# print(r.content)
# print(r)
