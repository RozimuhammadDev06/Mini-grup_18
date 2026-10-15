import os
import environ

env = environ.Env()

BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

DEBUG = int(os.environ.get("DEBUG", 1))

# Minimal default so `settings.REST_FRAMEWORK` exists immediately during
# module import. This ensures code that accesses `settings.REST_FRAMEWORK`
# (even during app auto-imports) won't raise AttributeError if later
# environment-specific settings fail to load.
if "REST_FRAMEWORK" not in globals():
    REST_FRAMEWORK = {
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    }

if DEBUG:
    print("DEBUG: ", DEBUG)
    print("Development settings")
    from .development import *
else:
    print("production settings start")
    from .production import *

# Ensure essential settings exist even if an imported settings module
# failed to define them (prevents runtime AttributeError when Django
# tries to access e.g. `settings.ROOT_URLCONF`).
if "ROOT_URLCONF" not in globals():
    ROOT_URLCONF = "config.urls"

# Provide a minimal `REST_FRAMEWORK` default to avoid AttributeError when
# code accesses `settings.REST_FRAMEWORK` before per-environment settings
# (development/production) are loaded or if they omitted the key.
if "REST_FRAMEWORK" not in globals():
    REST_FRAMEWORK = {
        # Prefer drf-spectacular's AutoSchema when available; individual
        # environments can override with their full REST_FRAMEWORK dict.
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    }

