# SPDX-FileCopyrightText: 2015, 2016 CERN.
# SPDX-FileCopyrightText: 2025 Graz University of Technology.
# SPDX-License-Identifier: BSD-3-Clause

"""Resolve JSON objects from different URLs."""

import importlib
from urllib.parse import urlsplit

import pluggy
from werkzeug.routing import Map

from . import hookspec


class JSONResolver:
    """Resolve JSON objects based on rules in URL map."""

    def __init__(self, plugins=None, entry_point_group=None):
        """Initialize resolver with various plugins and entry point group."""
        self.pm = pluggy.PluginManager("jsonresolver")
        self.pm.add_hookspecs(hookspec)
        for plugin in plugins or []:
            self.pm.register(importlib.import_module(plugin))
        if entry_point_group:
            self.pm.load_setuptools_entrypoints(entry_point_group)
        self.url_map = None

    def _build_url_map(self):
        """Build an URL map from registered plugins."""
        self.url_map = Map(host_matching=True)
        self.pm.hook.jsonresolver_loader(url_map=self.url_map)

    def resolve(self, url):
        """Resolve given URL and use registered loader."""
        if self.url_map is None:
            self._build_url_map()
        parts = urlsplit(url)
        loader, args = self.url_map.bind(parts.netloc).match(parts.path)
        return loader(**args)
