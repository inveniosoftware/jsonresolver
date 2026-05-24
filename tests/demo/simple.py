# SPDX-FileCopyrightText: 2015, 2016 CERN.
# SPDX-License-Identifier: BSD-3-Clause

"""Test plugin for JSON resolving using ``jsonresolver.route`` decorator."""

import jsonresolver


@jsonresolver.route("/test", host="localhost:4000")
def simple():
    """Return a fixed JSON."""
    return {"test": "test"}
