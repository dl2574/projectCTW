from django.apps import AppConfig
from django.contrib.staticfiles.apps import StaticFilesConfig


class BaseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "base"


class CustomStaticFilesConfig(StaticFilesConfig):
    # Extend default ignore patterns to exclude input.css, which is the
    # Tailwind source file and should never be served directly.
    ignore_patterns = StaticFilesConfig.ignore_patterns + ["input.css"]
