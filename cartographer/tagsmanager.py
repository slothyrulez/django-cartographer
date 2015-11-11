#! -*- coding: utf-8 -*-
"""
Manifest parsers
"""

from django.template import Context

from .registry import get_registry
from .errors import CartographerWebpackStatsError


class AssetTagsManagerBase(object):
    # TODO: Extend Node ??
    def __init__(self, manifest):
        self.manifest = manifest

    def render_fragment(self, template, context=None):
        """
        Render fragment using given django template
        """
        return template.render(context)

    def render(self):
        raise NotImplementedError


class AssetTagsManagerFromManifest(AssetTagsManagerBase):
    """
    Override AssetTagsManagerBase to implement management from the whole
    manifest
    """
    def __init__(self):
        self.manifest = get_registry()

    def get_template(self, bundle, asset):
        """
        Return the proper template for the given asset
        """
        try:
            # TODO: ugly uglu, use os
            return bundle.templates[asset.split(".")[1]]
        except KeyError as e:
            raise CartographerWebpackStatsError(e)

    def get_file(self, bundle, name):
        """
        Find and return asset file url given package name
        """
        asset = bundle[name]
        return asset.get("url", None)

    def render_bundle(self, bundle_name, kind=None):
        tags = []
        bundle = self.manifest[bundle_name]
        for asset_name, asset in bundle.filter_assets(kind):
            asset_url = self.get_file(bundle, asset_name)
            template = self.get_template(bundle, asset_url)
            tags.append(self.render_fragment(
                template, context=Context({"ASSET_URL": asset_url})))
        return "\n".join(tags)
