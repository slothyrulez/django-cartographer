#! -*- coding: utf-8 -*-

from django.apps import AppConfig

from .errors import BAD_CONFIG_ERROR
from .parsers import AssetsParserWebpackStats


def cartographer_cfg_check(app_configs, **kwargs):
    from django.conf import settings

    errors = []
    user_config = getattr(settings, 'CARTOGRAPHER', {})
    try:
        user_config = [dict({}, **cfg) for cfg in user_config.values()]
    except TypeError:
        errors.append(BAD_CONFIG_ERROR)
    return errors


class CartographerConfig(AppConfig):
    name = 'cartographer'
    verbose_name = "Django assets cartographer"

    def autodiscover(self):
        """
        Use settings to generate the registry of assets
        """
        from django.conf import settings

        user_config = getattr(settings, 'CARTOGRAPHER', {})
        for config_block in user_config:
            AssetsParserWebpackStats(config_block).parse()

    def ready(self):
        from django.core.checks import register, Tags
        register(Tags.compatibility)(cartographer_cfg_check)
        self.autodiscover()
