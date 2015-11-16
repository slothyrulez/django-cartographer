#! -*- coding: utf-8 -*-

import json
import time
import os
import re

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage

from .registry import get_registry, Bundle
from .defaults import DEFAULT_CONFIG, DEFAULT_BUNDLE_KEYS, UPDATABLE_BUNDLES
from .errors import CartographerWebpackStatsError, CartographerConfigError

try:
    _cartographer_cfg = getattr(settings, "CARTOGRAPHER")
except Exception as e:
    raise CartographerConfigError(e)


class AssetsParser(object):
    def __init__(self, name):
        self.origin = self.__class__.origin
        self.updatable = self.origin in UPDATABLE_BUNDLES
        self.registry = get_registry()
        self.name = name
        for prop in DEFAULT_BUNDLE_KEYS.get(self.origin):
            self._merge_cfg(self.name, prop)

    def _merge_cfg(self, bundle, prop):
        prop = prop.upper()
        bundle_cfg = _cartographer_cfg[self.origin].get(bundle, None)
        if not bundle_cfg:
            setattr(self, prop, DEFAULT_CONFIG[self.origin][prop])
        setattr(self, prop, bundle_cfg.get(prop, DEFAULT_CONFIG[self.origin][prop]))

    def get_origin(self):
        """
        Subclasses must override this method, it must return the origin of
        the 'parse'
        """
        raise NotImplementedError

    def parse(self):
        """
        Main action, expects subclasses override 'update'
        """
        self.update()
        if self.updatable:
            return self.get_origin()

    def deserialize(self):
        """
        Should return a dictionary with at least a name for the asset as
        the key and a path of the asset
        """
        raise NotImplementedError()

    def update(self):
        """
        Method adapting bundles/assets sources to registry
        """
        raise NotImplementedError()


class AssetsParserFile(AssetsParser):
    """
    Assets parser from file
    """
    origin = "FILE"

    def __init__(self, *args, **kw):
        raise NotImplementedError("TOBEDONE :)")


class AssetsParserWebpackStats(AssetsParser):
    """
    Assets parser from webpack stats loader
    """
    origin = "WEBPACK"

    def __init__(self, *args, **kw):
        super(AssetsParserWebpackStats, self).__init__(*args, **kw)
        if hasattr(self, 'IGNORE'):
            self.IGNORE = [re.compile(patt) for patt in self.IGNORE]

    def get_origin(self):
        """
        Return the origin parseable source
        """
        return self.SOURCE

    def get_source(self):
        """
        Webpack stats returns a json with a minimin structure
        # TODO: document structure
        """
        try:
            with open(self.SOURCE, 'r', encoding="utf-8") as json_file:
                return json.load(json_file)
        except IOError:
            raise IOError('Error reading {}. Are you sure webpack has \
                generated the file and the path is \
                correct?'.format(self.STATS_FILE))

    def filter_files(self, chunk):
        """
        webpack default config IGNORE
        """
        for _file in chunk:
            filename = _file["name"]
            ignore = any(regex.match(filename) for regex in self.IGNORE)
            if not ignore:
                realpath = os.path.join(self.BUNDLES_DIRNAME, filename)
                _file["url"] = staticfiles_storage.url(realpath)
                yield _file

    def _iter_chunks(self, manifest):
        for chunk in manifest:
            if chunk == self.name:
                yield chunk, manifest[chunk]

    def update(self):
        """
        Creates/Updates the registry from specified source
        """
        json_manifest = self.get_source()
        status = json_manifest.get('status')

        # Since webpack origin is updatable and now supoprt
        # inotify just will wait to receive the file update
        if status == "compiling":
            return

        # TODO: support timeouts
        # while status == 'compiling':
        #     time.sleep(self.poll_delay)
        #     json_manifest = self.get_source()
        #     status = json_manifest.get('status')

        if status == 'done':
            chunks = json_manifest['chunks']
            for chunk_name, chunk in self._iter_chunks(chunks):
                bundle = Bundle(name=chunk_name,
                                ORIGIN=self.origin,
                                IGNORE=self.IGNORE,
                                BUNDLES_DIRNAME=self.BUNDLES_DIRNAME,
                                SOURCE=self.SOURCE,
                                TAG_TEMPLATES=self.TAG_TEMPLATES)

                self.registry[chunk_name] = bundle
                for _file in self.filter_files(chunk):
                    asset_name = _file["name"]
                    asset_value = _file
                    bundle[asset_name] = asset_value

            return

        elif status == 'error':
            if 'file' not in json_manifest:
                json_manifest['file'] = ''
            error = """
            {error} in {file}
            {message}
            """.format(**json_manifest)
            raise CartographerWebpackStatsError(error)

        raise CartographerWebpackStatsError(
            "The stats file does not contain valid data. Make sure "
            "webpack-bundle-tracker plugin is enabled and try to run "
            "webpack again.")


def get_config():
    """
    """
    from django.conf import settings
    return getattr(settings, 'CARTOGRAPHER', {})


def autodiscover(updatables=False):
    """
    """
    user_config = get_config()
    for config_source, config_block in user_config.items():
        if updatables and config_source not in UPDATABLE_BUNDLES:
            continue
        if config_source == "WEBPACK":
            for bundle_name in config_block:
                AssetsParserWebpackStats(bundle_name).parse()


def rediscover():
    """
    """
    autodiscover(True)
