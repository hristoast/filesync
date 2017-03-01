#!/usr/bin/env python3
from fs.fs import DESCRIPTION, LICENSE, PROGNAME, VERSION
from setuptools import setup


with open('README.md', 'r') as r:
    rl = r.read()
    r.close()

setup(
    name=PROGNAME,
    version=VERSION,
    author="AUTHOR_NAME",
    author_email="AUTHOR_EMAIL",
    maintainer="AUTHOR_NAME",
    maintainer_email="AUTHOR_EMAIL",
    url="URL",
    description=DESCRIPTION,
    long_description=str(rl),
    download_url="URL",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: No Input/Output',
        'License :: OSI Approved :: GNU General Public License v3 or later'
        '(GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: System :: Operating System Kernels :: Linux',
        'Topic :: Utilities'],
    platforms=['linux2'],
    license=LICENSE,
    packages=["fs", ],
    entry_points={'console_scripts': [
        '{} = fs.fs:main'.format(PROGNAME), ]})
