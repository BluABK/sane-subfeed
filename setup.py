#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
        'cachetools>=2.1.0',
        'certifi>=2018.4.16',
        'chardet>=3.0.4',
        'click>=6.7',
        'configparser>=3.5.0',
        'google-api-python-client>=1.7.3',
        'google-auth>=1.5.0',
        'google-auth-httplib2>=0.0.3',
        'google-auth-oauthlib>=0.2.0',
        'httplib2>=0.11.3',
        'idna>=2.7',
        'oauthlib>=2.1.0',
        'Pillow>=5.2.0',
        'pyasn1>=0.4.3',
        'pyasn1-modules>=0.2.2',
        'PyQt5>=5.11.2',
        'PyQt5-sip>=4.19.11',
        'requests>=2.19.1',
        'requests-oauthlib>=1.0.0',
        'rsa>=3.4.2',
        'six>=1.11.0',
        'SQLAlchemy>=1.2.9',
        'tqdm>=4.23.4',     # FIXME: Should be optional/extras
        'uritemplate>=3.0.0',
        'urllib3>=1.23',
		'youtube-dl>=2018.7.29'

]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Acca",
    author_email='nikert.ludvik@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Returning the concept of sanity to the YouTube subscription feed.",
    entry_points={
        'console_scripts': [
            'sane_yt_subfeed=sane_yt_subfeed.cli:cli',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='sane_yt_subfeed',
    name='sane_yt_subfeed',
    packages=find_packages(include=['sane_yt_subfeed']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/Acccentor/sane_yt_subfeed',
    version='0.3.3',
    zip_safe=False,
)
