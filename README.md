# Django Rest Multi Token Auth
Work in progress, use at your own risk

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
urlpatterns = [
    ...
    url(r'^api/auth/', include('django_rest_multitokenauth.urls', namespace='multi_token_auth')),
    ...
]    
```


The following endpoints are provided:

 * `login` - takes username and password; on success an auth token is returned
 * `logout`
 * `reset_password` - request a reset password token 
 * `reset_password/confirm` - using a valid token, reset the password
 
## Signals

* ``reset_password_token_created(reset_password_token)`` Fired when a reset password token is generated
* ``pre_auth(username, password)`` - Fired when an authentication (login) is starting
* ``post_auth(user)`` - Fired on successful auth
