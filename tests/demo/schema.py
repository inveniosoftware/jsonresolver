# SPDX-FileCopyrightText: 2015, 2016 CERN.
# SPDX-License-Identifier: BSD-3-Clause

"""Test plugin for JSON schema resolving using decorator."""

import jsonresolver


@jsonresolver.route("/schema/<path:name>", host="localhost:4000")
def schema(name):
    """Return a fixed JSON ``schema``."""
    assert name == "authors.json"
    return {"type": "array"}
