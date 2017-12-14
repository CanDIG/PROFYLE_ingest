#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "docopt",
    "ga4gh-server",
    "numpy"
]

setup_requirements = [
]

test_requirements = [
]

setup(
    name='PROFYLE_ingest',
    version='0.1.0',
    description="Routines for ingesting PROFYLE metadata to GA4GH repository",
    long_description=readme + '\n\n' + history,
    author="Jonathan Dursi",
    author_email='jonathan@dursi.ca',
    url='https://github.com/ljdursi/PROFYLE_ingest',
    packages=find_packages(include=['PROFYLE_ingest']),
    entry_points={
        'console_scripts': [
            'PROFYLE_ingest = PROFYLE_ingest.profyle_ingest:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='PROFYLE_ingest',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    dependency_links=[
     "git+https://github.com/CanDIG/ga4gh-server.git@profyle#egg=ga4gh_server"
    ]
)
