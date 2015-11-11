# -*- coding: utf-8 -*-
"""
Asset manifest registry
"""

import json
import collections

from django.template.loader import get_template as loader_get_template

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
        self.get_templates()
        super(Bundle, self).__init__()

    def get_templates(self):
        " Initialize tempplates "
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
        if asset in self:
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
    def get_registry(self):
        return self

    def __getitem__(self, bundle):
        """ Returns bundle """
        try:
            return super(AssetManifestRegistry, self).__getitem__(bundle)
        except KeyError:
            raise NotRegisteredBundle(bundle)

    def __setitem__(self, bundle, value):
        # Non standard behaviour, asset is being overriden
        if bundle in self:
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
