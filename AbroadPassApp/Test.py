# -*- coding: utf-8 -*-
import requests
from requests.auth import HTTPBasicAuth
import json

#---------login---------#
login = 'http://localhost:8000/api/v1/user/login/'
data1 = {'username':'ojx1','password':'ojx9103123'}
head = {'Content-type':'application/json'}
r1 = requests.post(login,json.dumps(data1),headers=head)
print(r1.status_code)
print(r1.content)
print(r1.cookies)



#---------register---------#
# reg_url = 'http://localhost:8000/api/v1/user/register/'
# head = {'Content-type':'application/json'}
# data = {'username':'ojx1','password':'newpass'}
# r = requests.post(reg_url,json.dumps(data),headers=head)
# print(r.status_code)
# print(r.content)


#---------logout---------#
# reg_url = 'http://localhost:8000/api/v1/user/logout/'
# head = {'Content-type':'application/json'}
# #data = {'username':u'家兴','password':'newpass'}
# r = requests.get(reg_url,headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
# print(r.status_code)
# print(r.content)
# print(r.cookies)

#---------changepassword---------#
# login = 'http://localhost:8000/api/v1/user/changepassword/'
# data1 = {'oldpassword':'newpass','newpassword':'ojx9103123'}
# head = {'Content-type':'application/json'}
# r = requests.post(login,json.dumps(data1),headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
# print(r.status_code)
# print(r.content)
# print(r.cookies)


#---------view userprofile---------#
# url = 'http://localhost:8000/api/v1/userprofile/show/'
# head = {'Content-type':'application/json'}
# r = requests.get(url,headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
# if r.content =='':
#     print('没有值')
# else:
#     print(json.dumps(json.loads(r.content),indent=1))

#---------update userprofile---------#
url = 'http://localhost:8000/api/v1/userprofile/edit/'
data1 = {'qq':'584765203','mobile':'13416156631'}
head = {'Content-type':'application/json'}
r = requests.post(url,json.dumps(data1),headers=head,cookies={'sessionid':r1.cookies['sessionid'],'csrftoken':r1.cookies['csrftoken']})
print(r.status_code)
print(r.content)
print(r.cookies)