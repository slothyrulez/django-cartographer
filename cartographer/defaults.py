#! -*- coding: utf-8 -*-

"""
Default cartographer configuration
"""

DEFAULT_CONFIG = {
    'TAG_TEMPLATES': {
        "js": "cartographer/javascript_tag.html",
        "css": "cartographer/stylesheet_tag.html",
    },
    'ASSETS_STRICT': False,
    'BUNDLE_DIRNAME': 'webpack_bundles/',
    'STATS_FILE': 'webpack-stats.json',
    # FIXME: Explore usage of fsnotify
    'POLL_INTERVAL': 0.1,
    'IGNORE': ['.+\.hot-update.js', '.+\.map']
}

DEFAULT_BUNDLE_KEYS = DEFAULT_CONFIG.keys()
