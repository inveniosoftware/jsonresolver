# SPDX-FileCopyrightText: 2013 Julian Berman.
# SPDX-License-Identifier: MIT

"""Base for RefResolver."""

from collections import deque
from collections.abc import Mapping, MutableMapping, Sequence
from contextlib import contextmanager
from functools import lru_cache
from urllib.parse import unquote, urldefrag, urljoin, urlsplit

from jsonschema import exceptions
from jsonschema_specifications import REGISTRY as SPECIFICATIONS
from referencing.jsonschema import DRAFT202012
from rpds import HashTrieMap

_SUBSCHEMAS_KEYWORDS = ("$id", "id", "$anchor", "$dynamicAnchor")


class URIDict(MutableMapping):
    """
    Dictionary which uses normalized URIs as keys.

    # copy pasted from https://github.com/python-jsonschema/jsonschema 4.25.1
    """

    def normalize(self, uri):
        """Normalize."""
        return urlsplit(uri).geturl()

    def __init__(self, *args, **kwargs):
        """Construct."""
        self.store = dict()
        self.store.update(*args, **kwargs)

    def __getitem__(self, uri):
        """Get item."""
        return self.store[self.normalize(uri)]

    def __setitem__(self, uri, value):
        """Set item."""
        self.store[self.normalize(uri)] = value

    def __delitem__(self, uri):
        """Del item."""
        del self.store[self.normalize(uri)]

    def __iter__(self):
        """Iterate."""
        return iter(self.store)

    def __len__(self):  # pragma: no cover -- untested, but to be removed
        """Len."""
        return len(self.store)

    def __repr__(self):  # pragma: no cover -- untested, but to be removed
        """Repr."""
        return repr(self.store)


class RefResolverBase:
    """Implement custom remote URL resolver.

    copy pasted from https://github.com/python-jsonschema/jsonschema 4.25.1

    RefResolver is deprecated but it was easier to copy paste the code as to try
    to reproduce the behavior with the proposed referencing library
    """

    def __init__(
        self,
        base_uri,
        referrer,
        store=HashTrieMap(),
        cache_remote=True,
        handlers=(),
        urljoin_cache=None,
        remote_cache=None,
    ):
        """Construct."""
        if urljoin_cache is None:
            urljoin_cache = lru_cache(1024)(urljoin)
        if remote_cache is None:
            remote_cache = lru_cache(1024)(self.resolve_from_url)

        self.referrer = referrer
        self.cache_remote = cache_remote
        self.handlers = dict(handlers)

        self._scopes_stack = [base_uri]

        self.store = URIDict(
            (uri, each.contents) for uri, each in SPECIFICATIONS.items()
        )
        # _META_SCHEMAS is deprecated.
        # self.store.update((id, each.META_SCHEMA) for id, each in _META_SCHEMAS.items())
        self.store.update(store)
        self.store.update(
            (schema["$id"], schema)
            for schema in store.values()
            if isinstance(schema, Mapping) and "$id" in schema
        )
        self.store[base_uri] = referrer

        self._urljoin_cache = urljoin_cache
        self._remote_cache = remote_cache

    @classmethod
    def from_schema(  # noqa: D417
        cls,
        schema,
        id_of=DRAFT202012.id_of,
        *args,
        **kwargs,
    ):
        """
        Construct a resolver from a JSON schema object.

        Arguments:

            schema:

                the referring schema

        Returns:

            `_RefResolver`

        """
        return cls(base_uri=id_of(schema) or "", referrer=schema, *args, **kwargs)

    def resolve_from_url(self, url):
        """Resolve the given URL."""
        url, fragment = urldefrag(url)
        if not url:
            url = self.base_uri

        try:
            document = self.store[url]
        except KeyError:
            try:
                document = self.resolve_remote(url)
            except Exception as exc:
                raise exceptions._RefResolutionError(exc) from exc

        return self.resolve_fragment(document, fragment)

    @contextmanager
    def resolving(self, ref):
        """
        Resolve the given ``ref`` and enter its resolution scope.

        Exits the scope on exit of this context manager.

        Arguments:

            ref (str):

                The reference to resolve

        """
        url, resolved = self.resolve(ref)
        self.push_scope(url)
        try:
            yield resolved
        finally:
            self.pop_scope()

    def push_scope(self, scope):
        """
        Enter a given sub-scope.

        Treats further dereferences as being performed underneath the
        given scope.
        """
        self._scopes_stack.append(
            self._urljoin_cache(self.resolution_scope, scope),
        )

    def pop_scope(self):
        """
        Exit the most recent entered scope.

        Treats further dereferences as being performed underneath the
        original scope.

        Don't call this method more times than `push_scope` has been
        called.
        """
        try:
            self._scopes_stack.pop()
        except IndexError:
            raise exceptions._RefResolutionError(
                "Failed to pop the scope from an empty stack. "
                "`pop_scope()` should only be called once for every "
                "`push_scope()`",
            ) from None

    @property
    def resolution_scope(self):
        """Retrieve the current resolution scope."""
        return self._scopes_stack[-1]

    def resolve(self, ref):
        """Resolve the given reference."""
        url = self._urljoin_cache(self.resolution_scope, ref).rstrip("/")

        match = self._find_in_subschemas(url)
        if match is not None:
            return match

        return url, self._remote_cache(url)

    def _find_in_referrer(self, key):
        return self._get_subschemas_cache()[key]

    @lru_cache
    def _get_subschemas_cache(self):
        cache = {key: [] for key in _SUBSCHEMAS_KEYWORDS}
        for keyword, subschema in _search_schema(
            self.referrer,
            _match_subschema_keywords,
        ):
            cache[keyword].append(subschema)
        return cache

    @lru_cache  # noqa: B019
    def _find_in_subschemas(self, url):
        subschemas = self._get_subschemas_cache()["$id"]
        if not subschemas:
            return None
        uri, fragment = urldefrag(url)
        for subschema in subschemas:
            id = subschema["$id"]
            if not isinstance(id, str):
                continue
            target_uri = self._urljoin_cache(self.resolution_scope, id)
            if target_uri.rstrip("/") == uri.rstrip("/"):
                if fragment:
                    subschema = self.resolve_fragment(subschema, fragment)
                self.store[url] = subschema
                return url, subschema
        return None

    def resolve_fragment(self, document, fragment):
        """
        Resolve a ``fragment`` within the referenced ``document``.

        Arguments:

            document:

                The referent document

            fragment (str):

                a URI fragment to resolve within it

        """
        fragment = fragment.lstrip("/")

        if not fragment:
            return document

        if document is self.referrer:
            find = self._find_in_referrer
        else:

            def find(key):
                yield from _search_schema(document, _match_keyword(key))

        for keyword in ["$anchor", "$dynamicAnchor"]:
            for subschema in find(keyword):
                if fragment == subschema[keyword]:
                    return subschema
        for keyword in ["id", "$id"]:
            for subschema in find(keyword):
                if "#" + fragment == subschema[keyword]:
                    return subschema

        # Resolve via path
        parts = unquote(fragment).split("/") if fragment else []
        for part in parts:
            part = part.replace("~1", "/").replace("~0", "~")

            if isinstance(document, Sequence):
                try:  # noqa: SIM105
                    part = int(part)
                except ValueError:
                    pass
            try:
                document = document[part]
            except (TypeError, LookupError) as err:
                raise exceptions._RefResolutionError(
                    f"Unresolvable JSON pointer: {fragment!r}",
                ) from err

        return document


def _match_keyword(keyword):
    def matcher(value):
        """Matcher."""
        if keyword in value:
            yield value

    return matcher


def _match_subschema_keywords(value):
    for keyword in _SUBSCHEMAS_KEYWORDS:
        if keyword in value:
            yield keyword, value


def _search_schema(schema, matcher):
    """Breadth-first search routine."""
    values = deque([schema])
    while values:
        value = values.pop()
        if not isinstance(value, dict):
            continue
        yield from matcher(value)
        values.extendleft(value.values())
