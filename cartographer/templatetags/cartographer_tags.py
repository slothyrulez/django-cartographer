#! -*- coding:utf-8 -*-
"""
Assets tags
"""

from django.template.defaulttags import register

from cartographer.tagsmanager import AssetTagsManagerFromManifest


@register.simple_tag
def render_bundle(bundle_name, kind=None):
    """
    {% render_bundle "bundle_name" %}
    {% render_bundle "bundle_name" "js" %}
    {% render_bundle "bundle_name" "js, css" %}
    """
    # Django tags does not accept a list as arguments
    kind = (ext.strip() for ext in kind.split(",")) if kind else [""]
    return AssetTagsManagerFromManifest().render_bundle(bundle_name, kind)
