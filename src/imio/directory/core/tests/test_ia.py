# -*- coding: utf-8 -*-

from imio.directory.core.ia.browser.categorization_button_add import (
    IACategorizeAddForm,
    IACategorizeAddView,
)
from imio.directory.core.ia.browser.categorization_button_edit import (
    IACategorizeEditForm,
)
from imio.directory.core.ia.browser.views import ProcessCategorizeContentView
from imio.directory.core.testing import IMIO_DIRECTORY_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest import mock

import json
import unittest


class TestProcessCategorizeContentView(unittest.TestCase):
    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="Entity",
        )
        self.contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="Test Contact",
        )

    def _make_view(self, formdata=None):
        if formdata is None:
            formdata = {
                "form-widgets-IBasic-title": "Test Title",
                "form-widgets-subtitle": "Test Subtitle",
                "form-widgets-IBasic-description": "Test Description",
            }
        body = json.dumps({"formdata": formdata})
        view = ProcessCategorizeContentView(self.contact, self.request)
        view.request = mock.Mock()
        view.request.get.return_value = body
        view.request.response = self.request.response
        return view

    def test_get_all_text_combines_fields(self):
        view = self._make_view()
        result = view._get_all_text()
        self.assertEqual(result, "Test Title Test Subtitle Test Description")

    def test_get_all_text_missing_fields_returns_empty(self):
        view = self._make_view({})
        result = view._get_all_text()
        self.assertEqual(result, "")

    def test_get_all_text_partial_fields(self):
        view = self._make_view({"form-widgets-IBasic-title": "Only Title"})
        result = view._get_all_text()
        self.assertEqual(result, "Only Title")

    def test_get_all_text_strips_whitespace(self):
        view = self._make_view(
            {
                "form-widgets-IBasic-title": "",
                "form-widgets-subtitle": "",
                "form-widgets-IBasic-description": "",
            }
        )
        result = view._get_all_text()
        self.assertEqual(result, "")

    def test_process_category_returns_title_token_list(self):
        view = self._make_view()
        view._get_structured_data_from_vocabulary = mock.Mock(
            return_value=[{"title": "Health", "token": "health"}]
        )
        view._ask_categorization_to_ia = mock.Mock(
            return_value={"result": [{"title": "Health", "token": "health"}]}
        )
        result = view._process_category("Test text", {})
        self.assertEqual(result, [{"title": "Health", "token": "health"}])
        view._get_structured_data_from_vocabulary.assert_called_once_with(
            "imio.directory.vocabulary.ContactCategories"
        )

    def test_process_category_empty_result(self):
        view = self._make_view()
        view._get_structured_data_from_vocabulary = mock.Mock(return_value=[])
        view._ask_categorization_to_ia = mock.Mock(return_value={"result": []})
        result = view._process_category("Test text", {})
        self.assertEqual(result, [])

    def test_process_category_no_ia_response_returns_none(self):
        view = self._make_view()
        view._get_structured_data_from_vocabulary = mock.Mock(return_value=[])
        view._ask_categorization_to_ia = mock.Mock(return_value=None)
        result = view._process_category("Test text", {})
        self.assertIsNone(result)

    def test_process_category_empty_ia_response_returns_none(self):
        view = self._make_view()
        view._get_structured_data_from_vocabulary = mock.Mock(return_value=[])
        view._ask_categorization_to_ia = mock.Mock(return_value={})
        result = view._process_category("Test text", {})
        self.assertIsNone(result)

    def test_process_facilities_returns_title_token_list(self):
        view = self._make_view()
        view._get_structured_data_from_vocabulary = mock.Mock(
            return_value=[{"title": "Parking", "token": "parking"}]
        )
        view._ask_categorization_to_ia = mock.Mock(
            return_value={"result": [{"title": "Parking", "token": "parking"}]}
        )
        result = view._process_facilities("Test text", {})
        self.assertEqual(result, [{"title": "Parking", "token": "parking"}])
        view._get_structured_data_from_vocabulary.assert_called_once_with(
            "imio.directory.vocabulary.Facilities", self.contact
        )

    def test_process_facilities_no_ia_response_returns_none(self):
        view = self._make_view()
        view._get_structured_data_from_vocabulary = mock.Mock(return_value=[])
        view._ask_categorization_to_ia = mock.Mock(return_value=None)
        result = view._process_facilities("Test text", {})
        self.assertIsNone(result)

    def test_process_facilities_empty_ia_response_returns_none(self):
        view = self._make_view()
        view._get_structured_data_from_vocabulary = mock.Mock(return_value=[])
        view._ask_categorization_to_ia = mock.Mock(return_value={})
        result = view._process_facilities("Test text", {})
        self.assertIsNone(result)

    def test_process_specific_sets_category_and_facilities(self):
        view = self._make_view()
        view._process_category = mock.Mock(
            return_value=[{"title": "Health", "token": "health"}]
        )
        view._process_facilities = mock.Mock(
            return_value=[{"title": "Parking", "token": "parking"}]
        )
        results = {}
        returned = view._process_specific("some text", results)
        self.assertEqual(
            results["form-widgets-category"], [{"title": "Health", "token": "health"}]
        )
        self.assertEqual(
            results["form-widgets-facilities"],
            [{"title": "Parking", "token": "parking"}],
        )
        self.assertIs(returned, results)

    def test_process_specific_with_none_category(self):
        view = self._make_view()
        view._process_category = mock.Mock(return_value=None)
        view._process_facilities = mock.Mock(return_value=None)
        results = {}
        view._process_specific("some text", results)
        self.assertIsNone(results["form-widgets-category"])
        self.assertIsNone(results["form-widgets-facilities"])

    def test_call_returns_valid_json(self):
        view = self._make_view()
        with mock.patch.object(
            view, "_get_structured_data_from_vocabulary", return_value=[]
        ):
            with mock.patch.object(view, "_ask_categorization_to_ia", return_value={}):
                result = view()
        data = json.loads(result)
        self.assertTrue(data["ok"])
        self.assertIn("data", data)
        self.assertIn("message", data)

    def test_call_includes_category_and_facilities_in_data(self):
        view = self._make_view()
        category_result = [{"title": "Health", "token": "health"}]
        facilities_result = [{"title": "Parking", "token": "parking"}]

        def mock_voc(name, obj=None):
            return []

        def mock_ia(text, voc):
            return {}

        with mock.patch.object(
            view, "_get_structured_data_from_vocabulary", side_effect=mock_voc
        ):
            with mock.patch.object(
                view, "_ask_categorization_to_ia", side_effect=mock_ia
            ):
                with mock.patch.object(
                    view, "_process_category", return_value=category_result
                ):
                    with mock.patch.object(
                        view, "_process_facilities", return_value=facilities_result
                    ):
                        result = view()
        data = json.loads(result)
        self.assertEqual(data["data"]["form-widgets-category"], category_result)
        self.assertEqual(data["data"]["form-widgets-facilities"], facilities_result)


class TestIACategorizeAddForm(unittest.TestCase):
    def test_form_inherits_from_base(self):
        from imio.smartweb.common.ia.browser.categorization_button_add import (
            IACategorizeAddForm as BaseIACategorizeAddForm,
        )

        self.assertTrue(issubclass(IACategorizeAddForm, BaseIACategorizeAddForm))

    def test_add_view_uses_local_form(self):
        self.assertIs(IACategorizeAddView.form, IACategorizeAddForm)


class TestIACategorizeEditForm(unittest.TestCase):
    def test_form_inherits_from_base(self):
        from imio.smartweb.common.ia.browser.categorization_button_edit import (
            IACategorizeEditForm as BaseIACategorizeEditForm,
        )

        self.assertTrue(issubclass(IACategorizeEditForm, BaseIACategorizeEditForm))

    def test_page_edit_view_is_wrapped_form(self):
        from imio.directory.core.ia.browser.categorization_button_edit import (
            PageEditView,
        )

        self.assertTrue(callable(PageEditView))
