# -*- coding: utf-8 -*-
#
# This file is part of jsonresolver
# Copyright (C) 2015 CERN.
#
# jsonresolver is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

"""Define unit tests to test core functionality."""

import pytest
from demo.raising import EndpointCallDetected
from demo.raising_hook import HookRegistrationDetected

from jsonresolver import JSONResolver


def test_entry_point_group():
    """Test the entry point group loading."""
    resolver = JSONResolver(entry_point_group="espresso")
    assert resolver.resolve("http://localhost:4000/test") == {"test": "test"}


def test_plugins():
    """Test the plugins loading."""
    resolver = JSONResolver(plugins=["demo.simple"])
    assert resolver.resolve("http://localhost:4000/test") == {"test": "test"}


def test_plugin_lazy_execution():
    """Test the lazy evaluation of loaded plugin."""
    # Plugin code should be called (i.e. raise exception) on resolve method
    resolver = JSONResolver(plugins=["demo.raising"])
    with pytest.raises(EndpointCallDetected) as exc_info:
        resolver.resolve("http://localhost:4000/test")
    assert exc_info.type is EndpointCallDetected

    # Same as above but loaded using entry point
    resolver = JSONResolver(entry_point_group="raising")
    with pytest.raises(EndpointCallDetected) as exc_info:
        resolver.resolve("http://localhost:4000/test")
    assert exc_info.type is EndpointCallDetected


def test_plugin_lazy_execution_hooks():
    """Test the lazy evaluation of loaded plugin through hooks."""
    # Plugin code should be called (i.e. raise exception) on resolve method
    resolver = JSONResolver(plugins=["demo.raising_hook"])
    with pytest.raises(HookRegistrationDetected) as exc_info:
        resolver.resolve("http://localhost:4000/test")
    assert exc_info.type is HookRegistrationDetected

    # Same as above but loaded using entry point
    resolver = JSONResolver(entry_point_group="raising_hook")
    with pytest.raises(HookRegistrationDetected) as exc_info:
        resolver.resolve("http://localhost:4000/test")
    assert exc_info.type is HookRegistrationDetected
