# SPDX-FileCopyrightText: 2016 CERN.
# SPDX-License-Identifier: BSD-3-Clause

"""Test plugin for JSON resolving using ``jsonresolver.route`` decorator."""

import jsonresolver


@jsonresolver.route("/test", host="inveniosoftware.org")
def sameroute_as_simple():
    """Return a fixed JSON."""
    return {"test": "inveniosoftware.org"}
