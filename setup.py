#!/usr/bin/env python

from distutils.core import setup

from erlastic import __version__ as version

setup(
    name = 'erlastic',
    version = version,
    description = 'Erlastic',
    author = 'Samuel Stauffer',
    author_email = 'samuel@lefora.com',
    url = 'http://github.com/samuel/python-erlastic',
    packages = ['erlastic'],
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
