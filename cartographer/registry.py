# -*- coding: utf-8 -*-
"""
Asset manifest registry
"""
import json

from django.template.loader import get_template as loader_get_template

from .errors import (NotRegisteredBundle, NotRegisteredAsset,
    AlreadyRegisteredBundle, AlreadyRegisteredAsset)


class Bundle(object):
    def __init__(self, **kw):
        self._assets = {}
        for k, v in kw.items():
            setattr(self, k, v)
        self.get_templates()

    def get_templates(self):
        self.templates = {tag: loader_get_template(path)
                          for tag, path in self.TAG_TEMPLATES.items()}

    def to_registry(self):
        return {self.name: self}

    def filter_assets(self, kind=None):
        kind = kind or [""]
        extension = lambda name, ext: name.endswith(ext)
        for ext in kind:
            for name in self._assets:
                if extension(name, ext):
                    yield (name, self._assets[name])

    def get_asset(self, asset):
        try:
            return self._assets[asset]
        except KeyError:
            raise NotRegisteredAsset(asset)

    def has_asset(self, asset):
        return asset in self._assets

    def register_asset(self, asset, value):
        if self.has_asset(asset):
            raise AlreadyRegisteredAsset(asset)
        self._assets[asset] = value

    def unregister_asset(self, asset, value):
        if not self.has_asset(asset):
            raise NotRegisteredAsset(asset)
        del self._assets[asset]

    def update(self, assets):
        self._assets.update(**assets)

    def __str__(self):
        import pprint
        return pprint.pformat(self._assets)


class AssetManifestRegistry(object):
    """
    Manifest registry interface to store manifest entries
    """
    def __init__(self):
        # title_key (string) -> title_name (string)
        self._registry = {}
        self.override = False
        self.global_context = None

    def get_registry(self):
        return self._registry

    def get_asset(self, bundle, asset):
        _bundle = self.get_bundle(bundle)
        return _bundle.get_asset(asset)

    def has_asset(self, bundle, asset):
        _bundle = self.get_bundle(bundle)
        return _bundle.has_asset(asset)

    def get_bundle(self, bundle_name):
        try:
            return self._registry[bundle_name]
        except KeyError:
            raise NotRegisteredBundle(bundle_name)

    def has_bundle(self, bundle_name):
        return bundle_name in self._registry

    def register_bundle(self, bundle_name, bundle):
        if self.has_bundle(bundle_name):
            raise AlreadyRegisteredBundle(bundle_name)
        self._registry[bundle_name] = bundle

    def register_asset(self, bundle_name, asset, value):
        try:
            self._registry[bundle_name].register_asset(asset, value)
        except KeyError:
            raise NotRegisteredBundle(bundle_name)

    def unregister_bundle(self, bundle_name):
        if not self.has_bundle(bundle_name):
            raise NotRegisteredBundle(bundle_name)
        del self._registry[bundle_name]

    def unregister_asset(self, bundle_name, asset):
        try:
            self._registry[bundle_name].unregister_asset(asset)
        except KeyError:
            raise NotRegisteredBundle(bundle_name)

    def update(self, bundle):
        self._registry.update({bundle.name: bundle})

    def update_bundle(self, bundle_name, assets):
        try:
            self._registry[bundle_name].update(assets)
        except KeyError:
            raise NotRegisteredBundle(bundle_name)

    def json(self):
        json.dumps(self._registry)


manifest = AssetManifestRegistry()


def get_registry():
    return manifest
