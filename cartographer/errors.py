#! -*- coding: utf-8 -*-

from django.core.checks import Error

BAD_CONFIG_ERROR = Error(
    'Error while parsing CARTOGRAPHER configuration',
    hint='Is CARTOGRAPHER config valid?',
    obj='django.conf.settings.CAARTOGRAPHER',
    id='django-cartographer.E001',
)


class CartographerError(Exception):
    def __init__(self, value):
        self.value = value


class CartographerConfigError(Exception):
    pass


class CartographerWebpackStatsError(Exception):
    pass


class AlreadyRegistered(CartographerError):
    pass


class AlreadyRegisteredBundle(AlreadyRegistered):
    def __str__(self):
        return "BUNDLE {} already registered".format(repr(self.value))


class AlreadyRegisteredAsset(AlreadyRegistered):
    def __str__(self):
        return "ASSET {} already registered".format(repr(self.value))


class NotRegistered(CartographerError):
    pass


# TODO: List of registered
class NotRegisteredBundle(NotRegistered):
    def __str__(self):
        return "BUNDLE {} not registered".format(repr(self.value))

# TODO: List of registered
class NotRegisteredAsset(NotRegistered):
    def __str__(self):
        return "ASSET {} not registered".format(repr(self.value))


class AssetMapError(Exception):
    pass


class StaticfileAssetNotFound(Exception):
    pass
