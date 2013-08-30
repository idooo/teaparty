#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from teaparty import __version__

if sys.version_info <= (2, 4):
    error = "ERROR: boto requires Python Version 2.5 or above...exiting."
    print >> sys.stderr, error
    sys.exit(1)

setup(
    name='teaparty',
    version=__version__,
    packages=['teaparty'],
    scripts=['teaparty-daemon', 'teaparty-server'],
    url='',
    package_dir = {'':'server'},
    package_data = {'': ['db/*.db']},
    license='MIT',
    author='Alex Shteinikov',
    author_email='alex.shteinikov@gmail.com',
    description='',
    install_requires=[
        "Flask >= 0.10",
        #"gevent-socketio",
        "boto >= 2.11",
        "mock"
    ]
)
