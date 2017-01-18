import django.dispatch

reset_password_token_created = django.dispatch.Signal(providing_args=["reset_password_token"])
