# Django Rest Multi Token Auth
This django app is an extension for the Django Rest Framework (Version 3.4+).
It tries to overcome the limitation of Token Authentication, which only uses a single
token per user. 

## How to use

Django settings file:
```python
INSTALLED_APPS = (
    ...
    'django.contrib.auth',
    ...
    'rest_framework',
    ...
    'django_rest_multitokenauth',
    ...
)

```

Django REST Framework Settings:
```python
REST_FRAMEWORK = {
    ...
    'DEFAULT_AUTHENTICATION_CLASSES': [
        ...
        'django_rest_multitokenauth.coreauthentication.MultiTokenAuthentication',
        ...
    ],
    ...
}
```


Django url settings:
```python
from django.conf.urls import url, include


urlpatterns = [
    ...
    url(r'^api/auth/', include('django_rest_multitokenauth.urls', namespace='multi_token_auth')),
    ...
]    
```


The following endpoints are provided:

 * `login` - takes username and password; on success an auth token is returned
 * `logout`

## Signals

* ``pre_auth(username, password)`` - Fired when an authentication (login) is starting
* ``post_auth(user)`` - Fired on successful auth

## Tests

See folder [tests/](tests/). Basically, all endpoints are covered with multiple
unit tests.

Use this code snippet to run tests:
```bash
pip install -r requirements_test.txt
python setup.py install
cd tests
python manage.py test
```

## Cache Backend
If you want to use a cache for the session store, you can install [django-memoize](https://pythonhosted.org/django-memoize/) and add `'memoize'` to `INSTALLED_APPS`.

Then you need to use ``CachedMultiTokenAuthentication`` instead of ``MultiTokenAuthentication``.

```bash
pip install django-memoize
```

