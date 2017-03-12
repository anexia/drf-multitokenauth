import django.dispatch

reset_password_token_created = django.dispatch.Signal(
    providing_args=["reset_password_token"],
)

pre_auth = django.dispatch.Signal(providing_args=["username", "password"])

post_auth = django.dispatch.Signal(providing_args=["user"])
