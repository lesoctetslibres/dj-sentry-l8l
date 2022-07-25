from django.conf import settings

IGNORE_PATHS = getattr(settings, "SENTRY_L8L_IGNORE_PATHS", ["/api/bugs/"])
