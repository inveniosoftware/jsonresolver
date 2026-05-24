# SPDX-FileCopyrightText: 2015 CERN.
# SPDX-FileCopyrightText: 2025-2026 Graz University of Technology.
# SPDX-License-Identifier: BSD-3-Clause

"""Module that implements ``RefResolver`` factory using ``JSONResolver``.

The ``ref_resolver_factory`` uses an instance of ``JSONResolver`` for
implementation of remote URL resolver. The resolver is used to retrieve JSON
object based on registered plugins.

Example:
.. code-block:: python

   >>> from jsonschema import validate
   >>> from jsonresolver import JSONResolver
   >>> from jsonresolver.contrib.jsonschema import ref_resolver_factory
   >>> schema = {'$ref': 'http://localhost:4000/schema/authors.json#'}
   >>> json_resolver = JSONResolver(plugins=['tests.demo.schema'])
   >>> resolver_cls = ref_resolver_factory(json_resolver)
   >>> resolver = resolver_cls.from_schema(schema)
   >>> validate(['foo', 'bar'], schema, resolver=resolver)


"""

from werkzeug.exceptions import NotFound

from .base import RefResolverBase


def ref_resolver_factory(resolver):
    """Generate new RefResolver class that uses given resolver."""

    class RefResolver(RefResolverBase):
        def resolve_remote(self, uri):
            """Resolve remove uri using given resolver."""
            try:
                result = resolver.resolve(uri)
                if self.cache_remote:
                    self.store[uri] = result
                return result
            except NotFound:
                return super().resolve_remote(uri)

    return RefResolver
