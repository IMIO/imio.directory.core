.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

.. image:: https://github.com/IMIO/imio.directory.core/workflows/Tests/badge.svg
    :target: https://github.com/IMIO/imio.directory.core/actions?query=workflow%3ATests
    :alt: CI Status

.. image:: https://coveralls.io/repos/github/IMIO/imio.directory.core/badge.svg?branch=main
    :target: https://coveralls.io/github/IMIO/imio.directory.core?branch=main
    :alt: Coveralls

.. image:: https://img.shields.io/pypi/v/imio.directory.core.svg
    :target: https://pypi.python.org/pypi/imio.directory.core/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/imio.directory.core.svg
    :target: https://pypi.python.org/pypi/imio.directory.core
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/pyversions/imio.directory.core.svg?style=plastic   :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/l/imio.directory.core.svg
    :target: https://pypi.python.org/pypi/imio.directory.core/
    :alt: License


===================
imio.directory.core
===================

Directory product for 'Contacts authentic source' website

Features
--------

This products contains two content types: Entity & Contact.

An entity is bound to one or more belgian zip codes and contains editable geolocated contacts.

A contact can be exported to a vcard file using an object action.

This directory product is made to be used only by editors, to build the authentic source.
The website is then queried (RESTAPI) from other iMio websites.
Contacts are displayed in those sites by `imio.smartweb.core <https://github.com/IMIO/imio.smartweb.core>`_ contact section.


Examples
--------

Hopefully soon in production :-)


Documentation
-------------

TODO


Translations
------------

This product has been translated into

- French

The translation domain is ``imio.smartweb`` and the translations are stored in `imio.smartweb.locales <https://github.com/IMIO/imio.smartweb.locales>`_ package.


Installation
------------

Install imio.directory.core by adding it to your buildout::

    [buildout]

    ...

    eggs =
        imio.directory.core


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/collective/imio.directory.core/issues
- Source Code: https://github.com/collective/imio.directory.core


License
-------

The project is licensed under the GPLv2.
