#! -*- coding: utf-8 -*-

"""
Default cartographer configuration
"""

DEFAULT_CONFIG = {
    "WEBPACK": {
        'TAG_TEMPLATES': {
            "js": "cartographer/javascript_tag.html",
            "css": "cartographer/stylesheet_tag.html",
        },
        'BUNDLES_DIRNAME': 'webpack_bundles/',
        'SOURCE': 'webpack-stats.json',
        'IGNORE': ['.+\.hot-update.js', '.+\.map']
    }
}

DEFAULT_BUNDLE_KEYS = {
    k: v.keys() for k, v in DEFAULT_CONFIG.items()
}

UPDATABLE_BUNDLES = frozenset(["WEBPACK"])
