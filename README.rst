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

- https://annuaire.enwallonie.be


Documentation
-------------

Contact can be import from a CSV file via an action on the right Entity.
CSV Delimiter is ";"? and columns must be :

================  ============================================================
Column Index      Data
================  ============================================================
00                contact type
01                title
02                subtitle
03                description
04                street
05                number
06                complement
07                zipcode
08                city
09                country
10                vat number
11                latitude
12                longitude
13                phone label 1
14                phone type 1
15                phone number 1
16                phone label 2
17                phone type 2
18                phone number 2
19                phone label 3
20                phone type 3
21                phone number 3
22                mail label 1
23                mail type 1
24                mail address 1
25                mail label 2
26                mail type 2
27                mail address 2
28                mail label 3
29                mail type 3
30                mail address 3
31                url type 1
32                url link 1
33                url type 2
34                url link 2
35                url type 3
36                url link 3
37                topic 1
38                topic 2
39                topic 3
40                category 1
41                category 2
42                category 3
43                facility 1
44                facility 2
45                facility 3
46                iam 1
47                iam 2
48                iam 3
================  ============================================================


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
