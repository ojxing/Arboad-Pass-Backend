Abroad-Pass-Backend
==
 Backend for Arboad Pass App
 
 Tech
--
 * Django<br>
 * testypie

Getting started
--
Install Django, testypie<br>

    pip install django
    pip install django-tastypie
    
Database onfig and synchronized
--
Set up db in `setting.py`
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'example',
    }
}
```
Synchronize db

    python manage.py makemigrations
    python manage.py migrate

Run the server

    python manage.py runserver

Api Doc
--
 * [Api Doc](./doc/ApiDoc.md)
