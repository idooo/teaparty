#!/usr/bin/env python

import os, sys, glob, fnmatch

from teaparty import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def opj(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)

def find_data_files(srcdir, *wildcards, **kw):
    def walk_helper(arg, dirname, files):
        if '.svn' in dirname:
            return
        names = []
        lst, wildcards = arg
        for wc in wildcards:
            wc_name = opj(dirname, wc)
            for f in files:
                filename = opj(dirname, f)

                if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
                    names.append(filename)
        if names:
            lst.append( (dirname, names ) )

    file_list = []
    recursive = kw.get('recursive', True)
    if recursive:
        os.path.walk(srcdir, walk_helper, (file_list, wildcards))
    else:
        walk_helper((file_list, wildcards),
                    srcdir,
                    [os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
    return file_list

if sys.version_info <= (2, 4):
    error = "ERROR: boto requires Python Version 2.5 or above...exiting."
    print >> sys.stderr, error
    sys.exit(1)

data_files = find_data_files('teaparty/web/', '*.*')
data_files += find_data_files('teaparty/db/', '*.*')

requirements = ['Flask >= 0.10', 'boto >= 2.11']
test_requirements = ['mock']

# gevent-socket library for websocket support for flask is not building
# for windows so we will install it only on non-windows systems
if not (sys.platform.startswith('win32') or sys.platform.startswith('cygwin')):
    requirements.append('gevent-socketio')

setup(
    name='teaparty',
    version=__version__,
    packages=['teaparty'],
    scripts=['teaparty-daemon', 'teaparty-server'],
    url='',
    license='MIT',
    data_files=data_files,
    include_package_data=True,
    author='Alex Shteinikov',
    author_email='alex.shteinikov@gmail.com',
    description='',
    install_requires=requirements,
    test_suite='tests',
    tests_require=test_requirements
)
