# SPDX-FileCopyrightText: 2015 CERN.
# SPDX-FileCopyrightText: 2025-2026 Graz University of Technology.
# SPDX-License-Identifier: BSD-3-Clause

"""JSON data resolver with support for plugins."""

from .core import JSONResolver
from .decorators import route
from .hookimpl import hookimpl

__version__ = "0.5.1"

__all__ = (
    "JSONResolver",
    "hookimpl",
    "route",
    "__version__",
)
