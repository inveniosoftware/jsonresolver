# SPDX-FileCopyrightText: 2015 CERN.
# SPDX-License-Identifier: BSD-3-Clause

"""Test for detecting the lazy evaluation of hook-registered JSON resolver."""

import jsonresolver


class HookRegistrationDetected(Exception):
    """Raise this ``exception`` to detect when a hook is registered."""


@jsonresolver.hookimpl
def jsonresolver_loader(url_map):
    """Load the raising plugin as a Rule to URL map."""
    raise HookRegistrationDetected
