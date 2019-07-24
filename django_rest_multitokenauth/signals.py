import django.dispatch

__all__ = [
    'pre_auth',
    'post_auth',
]

# pre-auth signal
pre_auth = django.dispatch.Signal(providing_args=["username", "password"])

# post-auth signal
post_auth = django.dispatch.Signal(providing_args=["user"])
