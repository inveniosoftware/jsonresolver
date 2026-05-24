# SPDX-FileCopyrightText: 2015, 2016 CERN.
# SPDX-License-Identifier: BSD-3-Clause

"""Test adding JSON resolving rule using ``werkzeug.routing.Rule`` object."""

import requests
from werkzeug.routing import Rule

import jsonresolver


@jsonresolver.hookimpl
def jsonresolver_loader(url_map):
    """Load the resolver plugin as a Rule to URL map."""

    def endpoint(recid):
        return requests.get(
            "https://cds.cern.ch/record/{recid}?of=recjson".format(recid=recid)
        ).json

    url_map.add(Rule("/record/<recid>", endpoint=endpoint, host="cds.cern.ch"))
