#! -*- coding: utf-8 -*-

import json
import time
import os
import re

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage

from .registry import get_registry, Bundle
from .defaults import DEFAULT_CONFIG, DEFAULT_BUNDLE_KEYS
from .errors import CartographerWebpackStatsError, CartographerConfigError

try:
    _cartographer_cfg = getattr(settings, "CARTOGRAPHER")
except Exception as e:
    raise CartographerConfigError(e)


class AssetsParser(object):
    def __init__(self, name):
        self.registry = get_registry()
        self.name = name
        for prop in DEFAULT_BUNDLE_KEYS:
            self._merge_cfg(self.name, prop)

    def _merge_cfg(self, bundle, prop):
        prop = prop.upper()
        bundle_cfg = _cartographer_cfg.get(bundle, None)
        if not bundle_cfg:
            setattr(self, prop, DEFAULT_CONFIG[prop])
        setattr(self, prop, bundle_cfg.get(prop, DEFAULT_CONFIG[prop]))

    def parse(self):
        self.deserialize()
        self.update()

    def deserialize(self):
        """
        """
        raise NotImplementedError()

    def update(self):
        """
        Method adapting bundles/assets sources to registry
        """
        raise NotImplementedError()


class AssetsParserWebpackStats(AssetsParser):
    """
    Assets parser from webpack stats loader
    """
    # def __init__(self, origin, poll_delay, chunks, ignores, bundle_dirname):
    def __init__(self, *args, **kw):
        super(AssetsParserWebpackStats, self).__init__(*args, **kw)
        if hasattr(self, 'IGNORE'):
            self.IGNORE = [re.compile(patt) for patt in self.IGNORE]

    def deserialize(self):
        try:
            with open(self.STATS_FILE, 'r', encoding="utf-8") as json_file:
                return json.load(json_file)
        except IOError:
            raise IOError('Error reading {}. Are you sure webpack has \
                generated the file and the path is \
                correct?'.format(self.STATS_FILE))

    def filter_files(self, chunk):
        for _file in chunk:
            filename = _file["name"]
            ignore = any(regex.match(filename) for regex in self.IGNORE)
            if not ignore:
                realpath = os.path.join(self.BUNDLE_DIRNAME, filename)
                _file["url"] = staticfiles_storage.url(realpath)
                yield _file

    def filter_chunks(self, manifest):
        for chunk in manifest:
            if chunk == self.name:
                yield chunk, manifest[chunk]

    def update(self):
        json_manifest = self.deserialize()
        status = json_manifest.get('status')

        # TODO: support timeouts
        while status == 'compiling':
            time.sleep(self.poll_delay)
            json_manifest = self.deserialize()
            status = json_manifest.get('status')

        if status == 'done':
            chunks = json_manifest['chunks']
            for chunk_name, chunk in self.filter_chunks(chunks):
                bundle = Bundle(name=chunk_name,
                                IGNORE=self.IGNORE,
                                POLL_INTERVAL=self.POLL_INTERVAL,
                                BUNDLE_DIRNAME=self.BUNDLE_DIRNAME,
                                ASSETS_STRICT=self.ASSETS_STRICT,
                                STATS_FILE=self.STATS_FILE,
                                TAG_TEMPLATES=self.TAG_TEMPLATES)
                self.registry.register_bundle(chunk_name, bundle)
                for _file in self.filter_files(chunk):
                    self.registry.register_asset(chunk_name, _file["name"],
                                                 _file)
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
