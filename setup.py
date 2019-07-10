from setuptools import setup, find_packages
setup(
    name="Sane Subscription Feed",
    version="0.1.0-dev",
    packages=find_packages(),

    # FIXME: Currently rather specific versions due to lack of knowledge as to which versions may be incompatible
    install_requires=[
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
        'PySide2==5.13.0',
        'requests>=2.19.1',
        'requests-oauthlib>=1.0.0',
        'rsa>=3.4.2',
        'six>=1.11.0',
        'SQLAlchemy>=1.2.9',
        'uritemplate>=3.0.0',
        'urllib3>=1.23'
    ],

    author="BluABK",
    author_email="abk@blucoders.net",
    description="An independent 3rd party alternative to the algorithm plagued YouTube subscription feed",
    license="FIXME",    # FIXME: Figure out a license
    keywords="youtube google subscription feed independent blu abk",
    url="https://git.vpn/BluABK/sane-yt-subfeed",  # project home page, if any
    project_urls={
        "Bug Tracker": "https://git.vpn/BluABK/sane-yt-subfeed/issues",
        # "Documentation": "https://docs.example.com/HelloWorld/",   # FIXME: Add docs
        "Source Code": "https://git.vpn/BluABK/sane-yt-subfeed",
    }

    # TODO: could also include long_description, download_url, classifiers, etc.
)
