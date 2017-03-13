import django.dispatch

# pre-auth signal
pre_auth = django.dispatch.Signal(providing_args=["username", "password"])

# post-auth signal
post_auth = django.dispatch.Signal(providing_args=["user"])
