# Django Rest Multi Token Auth
Work in progress

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

 * `login`
 * `logout`