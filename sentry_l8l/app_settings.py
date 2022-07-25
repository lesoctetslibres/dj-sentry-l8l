from warnings import warn

from django.conf import settings

if not hasattr(settings, "SENTRY_L8L_IGNORE_PATHS"):
    warn(
        (
            "The /api/is-alive/ path is not down-sampled by default anymore."
            "Use SENTRY_L8L_IGNORE_PATHS to ignore it completely."
        ),
        DeprecationWarning,
    )


IGNORE_PATHS = getattr(settings, "SENTRY_L8L_IGNORE_PATHS", ["/api/bugs/"])
