# SPDX-FileCopyrightText: 2015, 2016 CERN.
# SPDX-License-Identifier: BSD-3-Clause

"""Test for detecting the lazy evaluation of decorated JSON resolver."""

import jsonresolver


class EndpointCallDetected(Exception):
    """Raise this ``exception`` to detect when a plugin is called in test."""


@jsonresolver.route("/test", host="localhost:4000")
def raising():
    """Raise an exception."""
    raise EndpointCallDetected
