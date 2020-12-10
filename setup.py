# -*- coding: utf-8 -*-
#
# This file is part of jsonresolver
# Copyright (C) 2015, 2016 CERN.
#
# jsonresolver is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""JSON data resolver with support for plugins."""

import os
import re

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'mock>=1.3.0',
    'pytest-cache>=1.0',
    'requests>=2.7.0',
    'pytest-invenio>=1.4.0'
]

extras_require = {
    'docs': [
        "Sphinx>=3",
    ],
    'jsonref': [
        'jsonref>=0.1',
    ],
    'jsonschema': [
        'jsonschema>=2.5.1',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
    'pytest-runner>=2.7.0',
]

install_requires = [
    'six>=1.12.0',
    'pluggy>=0.10.0,<1.0',
    'werkzeug>=1.0.0',
]

packages = find_packages()


# Get the version string. Cannot be done with import!
with open(os.path.join('jsonresolver', 'version.py'), 'rt') as f:
    version = re.search(
        '__version__\s*=\s*"(?P<version>.*)"\n',
        f.read()
    ).group('version')

setup(
    name='jsonresolver',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    url='https://github.com/inveniosoftware/jsonresolver',
    license='BSD',
    author='Invenio collaboration',
    author_email='info@inveniosoftware.org',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={},
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Flask',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Development Status :: 1 - Planning'
    ],
)
