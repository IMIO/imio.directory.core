# -*- coding: utf-8 -*-

from imio.directory.core.contents.entity.export import ordered_signifiant_columns
from imio.directory.core.testing import IMIO_DIRECTORY_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.formwidget.geolocation.geolocation import Geolocation
from zope.component import queryMultiAdapter

import io
import pandas
import unittest
from unittest.mock import MagicMock


class TestExport(unittest.TestCase):
    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_view_on_entity_without_contact(self):
        entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            id="entity",
        )
        view = queryMultiAdapter((entity, self.request), name="export")
        view()
        self.assertEqual(view.request.response.status, 204)

    def test_view_to_export_contacts(self):
        entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            id="entity",
        )
        contact1 = api.content.create(
            container=entity,
            type="imio.directory.Contact",
            id="contact1",
        )
        contact1.title = "Contact 1"
        contact1.type = "organization"
        contact1.iam = ["disabled_person", "newcomer"]
        contact1.private_phones = [
            {
                "label": "Private kamoulox phone",
                "type": "cell",
                "number": "+32496111111",
            }
        ]
        contact1.private_mails = [
            {
                "label": "Private kamoulox mail",
                "type": "home",
                "mail_address": "test@imio.be",
            }
        ]

        contact2 = api.content.create(
            container=entity,
            type="imio.directory.Contact",
            id="contact2",
        )
        contact2.title = "Contact 2"
        contact2.geolocation = Geolocation(50.2, 5.2)
        # "Commerces et entreprises"
        contact2.taxonomy_contact_category = ["cho96vl9ox"]
        contact3 = api.content.create(
            container=entity,
            type="imio.directory.Contact",
            id="contact3",
        )
        contact3.title = "Contact 3"
        contact3.geolocation = Geolocation(50.3, 5.3)
        contact3.schedule = schedule()
        automatically_populating_attributes = [
            "title_nl",
            "title_de",
            "title_en",
            "subtitle",
            "subtitle_nl",
            "subtitle_de",
            "subtitle_en",
            "description_nl",
            "description_de",
            "description_en",
            "street",
        ]
        contacts = [contact1, contact2, contact3]
        for column in ordered_signifiant_columns:
            if column in automatically_populating_attributes:
                for contact in contacts:
                    setattr(contact, column, f"{contact.id} : {column}")
        response_mock = MagicMock()
        response_mock.setHeader = MagicMock()
        response_mock.write = MagicMock()
        view = queryMultiAdapter((entity, self.request), name="export")
        view.request.response = response_mock
        view()
        response_mock.setHeader.assert_called_with("Content-Type", "text/csv")
        # Capture the written content
        written_content = response_mock.write.call_args[0][0]
        assert isinstance(written_content, bytes)
        csv_buffer = io.BytesIO(written_content)
        # Read the CSV data into a pandas DataFrame
        df = pandas.read_csv(csv_buffer, delimiter="|")

        # Check that the columns are present
        for column in ordered_signifiant_columns:
            self.assertIn(column, df.columns.to_list())

        for auto_attr in automatically_populating_attributes:
            for contact in contacts:
                self.assertIn(f"{contact.id} : {auto_attr}", df[auto_attr].to_list())

        type_contact1 = df.loc[df["title"] == "Contact 1", "type"].values[0]
        self.assertEqual(
            type_contact1,
            "['Organization (administrative service, business, professional, sports club, association, etc.)']",
        )
        iam_contact1 = df.loc[df["title"] == "Contact 1", "iam"].values[0]
        self.assertEqual(iam_contact1, "['Disabled person', 'Newcomer']")

        private_mails_contact1 = df.loc[
            df["title"] == "Contact 1", "private_mails"
        ].values[0]
        self.assertEqual(
            private_mails_contact1,
            "[{'label': 'Private kamoulox mail', 'type': 'home', 'mail_address': 'test@imio.be'}]",
        )

        private_phones_contact1 = df.loc[
            df["title"] == "Contact 1", "private_phones"
        ].values[0]
        self.assertEqual(
            private_phones_contact1,
            "[{'label': 'Private kamoulox phone', 'type': 'cell', 'number': '+32496111111'}]",
        )

        latitude_contact2 = df.loc[
            df["title"] == "Contact 2", "geolocation.latitude"
        ].values[0]
        self.assertEqual(latitude_contact2, 50.2)

        schedule_monday_comment_contact3 = df.loc[
            df["title"] == "Contact 3", "schedule.monday.comment"
        ].values[0]
        self.assertEqual(schedule_monday_comment_contact3, "Kamoulox")


def schedule():
    schedule = {
        "monday": {
            "comment": "Kamoulox",
            "morningstart": "8:00",
            "morningend": "12:00",
            "afternoonstart": "13:00",
            "afternoonend": "18:00",
        },
        "tuesday": {
            "comment": "",
            "morningstart": "",
            "morningend": "",
            "afternoonstart": "",
            "afternoonend": "",
        },
        "wednesday": {
            "comment": "",
            "morningstart": "",
            "morningend": "",
            "afternoonstart": "",
            "afternoonend": "",
        },
        "thursday": {
            "comment": "",
            "morningstart": "10:00",
            "morningend": "",
            "afternoonstart": "",
            "afternoonend": "18:30",
        },
        "friday": {
            "comment": "",
            "morningstart": "",
            "morningend": "",
            "afternoonstart": "",
            "afternoonend": "",
        },
        "saturday": {
            "comment": "",
            "morningstart": "",
            "morningend": "",
            "afternoonstart": "",
            "afternoonend": "",
        },
        "sunday": {
            "comment": "Always closed sunday",
            "morningstart": "",
            "morningend": "",
            "afternoonstart": "",
            "afternoonend": "",
        },
    }
    return schedule
