# Django Rest Multi Token Auth

[![PyPI](https://img.shields.io/pypi/v/django-rest-multitokenauth)](https://pypi.org/project/django-rest-multitokenauth/)
[![Build Status](https://travis-ci.org/anexia-it/django-rest-multitokenauth.svg?branch=master)](https://travis-ci.org/anexia-it/django-rest-multitokenauth)
[![Codecov](https://img.shields.io/codecov/c/gh/anexia-it/django-rest-multitokenauth)](https://codecov.io/gh/anexia-it/django-rest-multitokenauth)

This django app is an extension for the Django Rest Framework.
It tries to overcome the limitation of Token Authentication, which only uses a single token per user. 

## How to use

Install:
```bash
pip install django-rest-multitokenauth
```

Add ``'django_rest_multitokenauth'`` to your ``INSTALLED_APPS`` in your Django settings file:
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

Configure Django REST Framework to use ``'django_rest_multitokenauth.coreauthentication.MultiTokenAuthentication'``:
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


And add the auth urls to your Django url settings:
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
pip install tox
tox
```

## Cache Backend

If you want to use a cache for the session store, you can install [django-memoize](https://pythonhosted.org/django-memoize/) and add `'memoize'` to `INSTALLED_APPS`.

Then you need to use ``CachedMultiTokenAuthentication`` instead of ``MultiTokenAuthentication``.

```bash
pip install django-memoize
```

## Django Compatibility Matrix

If your project uses an older verison of Django or Django Rest Framework, you can choose an older version of this project.

| This Project | Python Version | Django Version | Django Rest Framework |
|--------------|----------------|----------------|-----------------------|
| 1.4.*        | 3.5+           | 2.2+, 3.0+     | 3.9, 3.10, 3.11, 3.12 |
| 1.3.*        | 2.7, 3.4+      | 1.11, 2.0+     | 3.6, 3.7, 3.8         |
| 1.2.*        | 2.7, 3.4+      | 1.8, 1.11, 2.0+| 3.6, 3.7, 3.8         |

Make sure to use at least `DRF 3.10` when using `Django 3.0` or newer.


## Changelog / Releases

All releases should be listed in the [releases tab on github](https://github.com/anexia-it/django-rest-multitokenauth/releases).

See [CHANGELOG.md](CHANGELOG.md) for a more detailed listing.


## License

This project is published with the [BSD 3 Clause License](LICENSE). See [https://choosealicense.com/licenses/bsd-3-clause-clear/](https://choosealicense.com/licenses/bsd-3-clause-clear/) for more information about what this means.
