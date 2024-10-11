# Django Rest Multi Token Auth

[![PyPI](https://img.shields.io/pypi/v/drf-multitokenauth)](https://pypi.org/project/drf-multitokenauth/)
[![Test status](https://github.com/anexia/drf-multitokenauth/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/anexia/drf-multitokenauth/actions/workflows/test.yml)
[![Codecov](https://img.shields.io/codecov/c/gh/anexia/drf-multitokenauth)](https://codecov.io/gh/anexia/drf-multitokenauth)

This django app is an extension for the Django Rest Framework.
It tries to overcome the limitation of Token Authentication, which only uses a single token per user. 

## How to use

Install:
```bash
pip install drf-multitokenauth
```

Add ``'drf_multitokenauth'`` to your ``INSTALLED_APPS`` in your Django settings file:
```python
INSTALLED_APPS = (
    ...
    'django.contrib.auth',
    ...
    'rest_framework',
    ...
    'drf_multitokenauth',
    ...
)

```

Configure Django REST Framework to use ``'drf_multitokenauth.coreauthentication.MultiTokenAuthentication'``:
```python
REST_FRAMEWORK = {
    ...
    'DEFAULT_AUTHENTICATION_CLASSES': [
        ...
        'drf_multitokenauth.coreauthentication.MultiTokenAuthentication',
        ...
    ],
    ...
}
```


And add the auth urls to your Django url settings:
```python
from django.conf.urls import include
from django.urls import re_path


urlpatterns = [
    ...
    re_path(r'^api/auth/', include('drf_multitokenauth.urls', namespace='multi_token_auth')),
    ...
]    
```


The following endpoints are provided:

 * `login` - takes username, password and an optional token_name; on success an auth token is returned
 * `logout`

## Signals

* ``pre_auth(username, password)`` - Fired when an authentication (login) is starting
* ``post_auth(user)`` - Fired on successful auth

## Tests

See folder [tests/](tests/). Basically, all endpoints are covered with multiple
unit tests.

Follow below instructions to run the tests.
You may exchange the installed Django and DRF versions according to your requirements. 
:warning: Depending on your local environment settings you might need to explicitly call `python3` instead of `python`.
```bash
# install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# setup environment
pip install -e .
python setup.py install

# run tests
cd tests && python manage.py test
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
| 2.1.*        | 3.9+           | 4.2, 5.0, 5.1  | 3.15                  |
| 2.0.*        | 3.7+           | 3.2, 4.0, 4.1  | 3.12, 3.13            |
| 1.5.*        | 3.7+           | 3.2, 4.0, 4.1  | 3.12, 3.13            |
| 1.4.*        | 3.6+           | 2.2, 3.2       | 3.9, 3.10, 3.11, 3.12 |
| 1.3.*        | 2.7, 3.4+      | 1.11, 2.0      | 3.6, 3.7, 3.8         |
| 1.2.*        | 2.7, 3.4+      | 1.8, 1.11, 2.0 | 3.6, 3.7, 3.8         |

Make sure to use at least `DRF 3.10` when using `Django 3.0` or newer.

Releases prior to `2.0.0` where published as [django-rest-multitokenauth](https://pypi.org/project/django-rest-multitokenauth/).
Newer releases are published as [drf-multitokenauth](https://pypi.org/project/drf-multitokenauth/).

## Migrating from 1.x to 2.x

1. Uninstall `django-rest-multitokenauth`
2. Install `drf-multitokenauth`
3. Run the migration SQL bellow:
    ```
    ALTER TABLE django_rest_multitokenauth_multitoken RENAME to drf_multitokenauth_multitoken;
    UPDATE django_migrations SET app = 'drf_multitokenauth' WHERE app = 'django_rest_multitokenauth';
    UPDATE django_content_type SET app_label = 'drf_multitokenauth' WHERE app_label = 'django_rest_multitokenauth';
    ```
4. Run Django migrations

## Changelog / Releases

All releases should be listed in the [releases tab on github](https://github.com/anexia/drf-multitokenauth/releases).

See [CHANGELOG.md](CHANGELOG.md) for a more detailed listing.


## License

This project is published with the [BSD 3 Clause License](LICENSE). See [https://choosealicense.com/licenses/bsd-3-clause-clear/](https://choosealicense.com/licenses/bsd-3-clause-clear/) for more information about what this means.
