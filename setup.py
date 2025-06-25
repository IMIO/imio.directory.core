# -*- coding: utf-8 -*-
"""Installer for the imio.directory.core package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="imio.directory.core",
    version="1.2.20",
    description="Core product for iMio contacts Directory websites",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: 6.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone CMS",
    author="Christophe Boulanger",
    author_email="christophe.boulanger@imio.be",
    url="https://github.com/imio/imio.directory.core",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/imio.directory.core",
        "Source": "https://github.com/imio/imio.directory.core",
        "Tracker": "https://github.com/imio/imio.directory.core/issues",
        # 'Documentation': 'https://imio.directory.core.readthedocs.io/en/latest/',
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["imio", "imio.directory"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "setuptools",
        "z3c.jbot",
        "z3c.unconfigure",
        "plone.api>=1.8.4",
        "plone.gallery",
        "plone.restapi",
        "plone.app.dexterity",
        "plone.app.discussion",
        "plone.app.imagecropping",
        "pandas",
        "collective.taxonomy",
        "embeddify",
        "imio.smartweb.common",
        "imio.smartweb.locales",
        "collective.instancebehavior",
        "collective.z3cform.datagridfield>=2.0",
        "collective.geolocationbehavior",
        "collective.monkeypatcher",
        "collective.schedulefield",
        "vobject",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            "plone.testing>=5.0.0",
            "plone.app.contenttypes",
            "plone.app.robotframework[debug]",
            "requests-mock",
            "beautifulsoup4",
            "plone.restapi[test]",
        ],
    },
    entry_points="""""",
)
