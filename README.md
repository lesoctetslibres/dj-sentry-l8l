# sentry-l8l

## Quick Start

1. Install with pip:

   ```shell
   pip install "dj-sentry-l8l @ git+https://github.com/lesoctetslibres/dj-sentry-l8l.git@master"
   ```

2. Sentry Configuration is only possible via environment variables:

   - `SENTRY_DSN`, `SENTRY_ENVIRONMENT`, `SENTRY_RELEASE` are read directly by
     sentry-sdk
   - `SENTRY_TRACES_SAMPLE_RATE` is specific to senty-l8l and defaults to `0.1`;
     valid values range from 0 (disable performance monitoring) to 1.

3. (optional) Add the `sentry_tunnel` view to your url config:

   ```py
   from sentry_l8l import sentry_tunnel

   urlpatterns += [
       path("bugs/", sentry_tunnel),
   ]
   ```

   You can now use the `tunnel` option on the frontend, e.g.:

   ```js
   Sentry.init({
     dsn: "https://32a12d35ebf54ce8ac296e301ff0488e@o1082473.ingest.sentry.io/6095369",
     tunnel: "/bugs/",
   });
   ```

   WARNING: the DSN of the frontend must be the same as the one configured for
   the backend (SENTRY_DSN)

4. Configure optional settings:

   - `SENTRY_L8L_IGNORE_PATHS = ["/api/bugs/", "/api/path-to-ignore/]`
     Hint: the values to put in this setting are the transaction names as displayed in sentry.
   - `SENTRY_L8L_IGNORE_CELERY_TASKS = ["my_project.celery.task_to_ignore"]`
     Hint: the values to put in this setting are the transaction names as displayed in sentry.
