# SPDX-FileCopyrightText: 2015 CERN.
# SPDX-License-Identifier: BSD-3-Clause

"""Define hook specification."""

import pluggy

hookspec = pluggy.HookspecMarker("jsonresolver")


@hookspec
def jsonresolver_loader(url_map):
    """Retrieve JSON document."""
    pass  # pragma: no cover
