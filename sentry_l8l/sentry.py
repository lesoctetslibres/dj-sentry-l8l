import os
from json import decoder
from warnings import warn

import requests
import sentry_sdk
from django.conf import settings
from django.http import request
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger
from urllib3.util import parse_url

from . import app_settings


#   deepcode ignore DisablesCSRFProtection: Sentry proxy, no action performed
@csrf_exempt
def sentry_tunnel(request: request.HttpRequest):
    """
    sentry_tunnel endpoint helps defeating ad-blockers.

    Sentry requests are blocked by ad-blockers. This endpoint allows to use sentry on the frontend
    by creating a proxy.
    """

    lines = request.body.splitlines()
    header = decoder.JSONDecoder().decode(lines[0].decode())
    allowed_dsn = os.environ.get("SENTRY_DSN", None)
    if allowed_dsn:
        allowed_dsn_url = parse_url(allowed_dsn)
        allowed_host = allowed_dsn_url.host
    else:
        # no dsn, just silently ignore
        return HttpResponse(status=200)

    if "dsn" in header:
        uri = parse_url(header["dsn"])
        if uri.host != allowed_host:
            raise Exception(f"Invalid Sentry DSN host: {uri.host}")
        project_id = uri.path.strip("/")
        if project_id != allowed_dsn_url.path.strip("/"):
            raise Exception(f"Invalid Sentry DSN project: {project_id}")
        res = requests.post(
            f"https://{uri.host}/api/{project_id}/envelope/?sentry_key={uri.auth}",
            data=request.body,
        )

        return HttpResponse(content=res.content, status=res.status_code)

    return HttpResponse(status=400)


class TracesSampler:
    def __init__(self, default_sampling_rate=1.0):
        self.default_sampling_rate = float(default_sampling_rate)
        if not hasattr(settings, "SENTRY_L8L_IGNORE_PATHS"):
            warn(
                (
                    "The /api/is-alive/ path is not down-sampled by default anymore."
                    "Use SENTRY_L8L_IGNORE_PATHS to ignore it completely."
                ),
                DeprecationWarning,
            )

    def __call__(self, sampling_context):
        if (
            "wsgi_environ" in sampling_context
            and sampling_context["wsgi_environ"]["PATH_INFO"] in app_settings.IGNORE_PATHS
        ):
            return 0
        else:
            return self.default_sampling_rate

    @classmethod
    def get_sentry_sdk_init_kwargs(cls, default_sampling_rate):
        if default_sampling_rate:
            return {"traces_sampler": cls(default_sampling_rate=default_sampling_rate)}
        else:
            return {"traces_sample_rate": 0}


def init(default_sampling_rate=None, release=None):
    if os.environ.get("SENTRY_ENVIRONMENT", None):
        ignore_logger("django.security.DisallowedHost")

        if default_sampling_rate is None:
            default_sampling_rate = os.environ.get("SENTRY_TRACES_SAMPLE_RATE", 0.1)
        sentry_sdk.init(
            # set SENTRY_DSN environment variable to use
            # (recommended: also set SENTRY_ENVIRONMENT to 'prod' or 'staging')
            integrations=[DjangoIntegration()],
            release=release,
            # If you wish to associate users to errors (assuming you are using
            # django.contrib.auth) you may enable sending PII data.
            send_default_pii=True,
            **TracesSampler.get_sentry_sdk_init_kwargs(default_sampling_rate=default_sampling_rate),
        )

        sentry_sdk.set_tag("service", "backend")
