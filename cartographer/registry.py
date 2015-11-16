# -*- coding: utf-8 -*-
"""
Asset manifest registry
"""

import json
import collections

from django.template.loader import get_template as loader_get_template

from .defaults import UPDATABLE_BUNDLES
from .errors import (NotRegisteredBundle, NotRegisteredAsset,
                     AlreadyRegisteredBundle, AlreadyRegisteredAsset)


class Bundle(collections.UserDict):
    """
    Holds logic of the bundle
    Overrides collections.UserDict to behave like a common dict
    """
    def __init__(self, **kw):
        """
        Bundle initializes with "settings", keywords passed on initialization
        will be used as object attributes, not data
        """
        for k, v in kw.items():
            self.__setattr__(k, v)
        self.updatable = self.ORIGIN in UPDATABLE_BUNDLES
        self.get_templates()
        super(Bundle, self).__init__()

    def get_templates(self):
        """
        Initialize templates
        """
        # TODO: Raise raise improperly configured
        self.templates = {tag: loader_get_template(path)
                          for tag, path in self.TAG_TEMPLATES.items()}

    def to_registry(self):
        # TODO: check is used ? is needed ?
        return {self.name: self}

    def filter_assets(self, kind=None):
        """
        Filter contents of the bundle by extension
        """
        # TODO: Use a proper/better check of the extension
        kind = kind or [""]
        extension = lambda name, ext: name.endswith(ext)
        for ext in kind:
            for name in self:
                if extension(name, ext):
                    yield (name, self[name])

    def __getitem__(self, asset):
        try:
            return super(Bundle, self).__getitem__(asset)
        except KeyError:
            raise NotRegisteredAsset(asset)

    def __setitem__(self, asset, value):
        # Non standard behaviour, asset is being override

        if not self.updatable and asset in self:
            raise AlreadyRegisteredAsset(asset)
        super(Bundle, self).__setitem__(asset, value)

    def __delitem__(self, asset):
        if asset not in self:
            raise NotRegisteredAsset(asset)
        super(Bundle, self).__delitem__(asset)


class AssetManifestRegistry(collections.UserDict):
    """
    Manifest registry interface to store manifest entries
    """
    def __init__(self, *args, **kw):
        """
        Hold a registry of incoming
        """
        super(AssetManifestRegistry, self).__init__(*args, **kw)

    def get_registry(self):
        return self

    def filter_updatable(self):
        """
        Updatable bundles are those whose assets can change
        """
        for bundle_name, bundle in self.items():
            if bundle.ORIGIN in UPDATABLE_BUNDLES:
                yield (bundle_name, bundle)

    def get_updatable_sources(self):
        return (getattr(bundle, "SOURCE", None)
                for bundle_name, bundle in self.filter_updatable())

    def __getitem__(self, bundle):
        """ Returns bundle """
        try:
            return super(AssetManifestRegistry, self).__getitem__(bundle)
        except KeyError:
            raise NotRegisteredBundle(bundle)

    def __setitem__(self, bundle, value):
        # Non standard behaviour, asset is being overriden
        if bundle in self and not self[bundle].updatable:
            raise AlreadyRegisteredBundle(bundle)
        super(AssetManifestRegistry, self).__setitem__(bundle, value)

    def __delitem__(self, bundle):
        """ Delete bundle """
        if bundle not in self:
            raise NotRegisteredBundle(bundle)
        super(AssetManifestRegistry, self).__delitem__(bundle)

    def serialize_json(self):
        json.dumps(self)

manifest = AssetManifestRegistry()


def get_registry():
    return manifest
