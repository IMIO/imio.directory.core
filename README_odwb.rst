=========================
Send contacts to ODWB
=========================

This document tells how to configure a directory site to send contacts and
entities to ODWB (Open Data Wallonie-Bruxelles, https://www.odwb.be).

.. contents::
   :local:


ODWB datasets
=============

The site sends data to 4 ODWB datasets:

==================================================  ==========================
ODWB dataset id                                      Content
==================================================  ==========================
``contacts-en-wallonie``                             Contacts (production)
``staging-contacts-en-wallonie``                     Contacts (staging)
``entites-des-contacts-en-wallonie``                 Entities (production)
``staging-entites-des-contacts-en-wallonie``         Entities (staging)
==================================================  ==========================

On ODWB, make sure that:

- the dataset id is exactly the name in the table above;
- the real-time push ("temps réel") is enabled on the dataset source;
- you have the pushkey of the dataset source.


Registry records
================

Set these records in the Plone registry (``@@configuration_registry``).
Each pushkey must be the pushkey of the dataset with the same name.

Pushkeys (TextLine):

- ``imio.directory.core.odwb_contacts-en-wallonie_pushkey``
- ``imio.directory.core.odwb_staging-contacts-en-wallonie_pushkey``
- ``imio.directory.core.odwb_entites-des-contacts-en-wallonie_pushkey``
- ``imio.directory.core.odwb_staging-entites-des-contacts-en-wallonie_pushkey``

Staging flag (Bool, see `Production or staging`_):

- ``imio.smartweb.common.activate_sending_data_to_odwb_for_staging``

The pushkey records are in ``imio.directory.core``. The staging flag is in
``imio.smartweb.common``.

To read a record with the REST API::

    curl -u admin:xxx -H "Accept: application/json" \
      "https://<site>/@registry/imio.directory.core.odwb_staging-contacts-en-wallonie_pushkey"


Production or staging
=====================

Two different checks control the sending.

1. Is the site in staging or local?

   The site URL tells it (``is_staging_or_local`` in ``imio.smartweb.common``):

   - ``https`` URL that contains ``staging`` or ``preprod``: staging;
   - ``http`` URL on ``localhost`` or ``127.0.0.1``: local;
   - all other URLs: production.

2. Which dataset receives the data?

   The ``activate_sending_data_to_odwb_for_staging`` flag tells it. The site
   URL has no effect on this choice.

========== ===== =========================================================
Site       Flag  Result
========== ===== =========================================================
staging    False Nothing is sent. The log shows "Don't send odwb data when
                 we are in staging or local environment".
staging    True  Data goes to the ``staging-*`` datasets.
production False Data goes to the production datasets.
production True  Data goes to the ``staging-*`` datasets. Do not do this.
========== ===== =========================================================


Automatic sending
=================

When the site can send, these events send one contact to ODWB:

- a contact is published;
- a published contact is modified;
- a published contact is moved to another entity.

These events delete one contact on ODWB:

- a contact goes back to the ``private`` state;
- a contact is deleted.


Manual sending (all contacts)
=============================

Use these REST endpoints to send all the data again, for example after you
create a new dataset. Use the ``GET`` method and the
``Accept: application/json`` header.

``@odwb``
    On the site root: sends all published contacts.
    On an entity: sends the published contacts of this entity.
    On a contact: sends this contact.

``@odwb_entities``
    Sends all published entities.

Example::

    curl -u admin:xxx -H "Accept: application/json" \
      "https://annuaire.staging.imio.be/@odwb"

The request is synchronous. The site sends the data by batches of 1000
items. With many contacts, a proxy can stop the request before the end.
Look at the instance log in this case (one line per batch).


Read the response
=================

The endpoint returns a summary::

    {
        "service": "staging-contacts-en-wallonie",
        "total": 53,
        "sent": 53,
        "batches": [
            {"size": 53, "status_code": 200, "response": ""}
        ]
    }

``service``
    The ODWB dataset that receives the data.
``total``
    The number of items to send.
``sent``
    The number of items in the batches that ODWB accepted (HTTP 2xx).
``batches``
    For each batch: the number of items, the HTTP status code from ODWB and
    the response text from ODWB.

If the response is ``null``, the site did not send anything. Look at the
staging flag.


Troubleshooting
===============

``null`` response, or "Don't send odwb data..." in the log
    The site is in staging or local and the staging flag is ``False``.

``status_code`` is ``401``
    ODWB does not accept the pushkey. Make sure that the pushkey record is
    not empty and that it is the pushkey of the correct dataset (not the
    production one, not an old one). You can test a pushkey directly::

        curl -s -o /dev/null -w "%{http_code}\n" -X POST \
          -H "Content-Type: application/json" -d '[]' \
          "https://www.odwb.be/api/push/1.0/staging-contacts-en-wallonie/temps_reel/push/?pushkey=<PUSHKEY>"

``status_code`` is ``null``
    The site cannot connect to ODWB (connection error or timeout). The
    ``response`` field gives the reason.

``sent`` is lower than ``total``
    One or more batches failed. Look at the ``status_code`` and ``response``
    of each batch.
