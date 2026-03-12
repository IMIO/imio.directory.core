from imio.smartweb.common.ia.browser.views import BaseProcessCategorizeContentView

import json


class ProcessCategorizeContentView(BaseProcessCategorizeContentView):

    def _get_all_text(self):
        all_text = ""
        raw = self.request.get("BODY")
        data = json.loads(raw)
        contact_title = data.get("formdata").get("form-widgets-IBasic-title", "")
        contact_subtitle = data.get("formdata").get("form-widgets-subtitle", "")
        contact_description = data.get("formdata").get(
            "form-widgets-IBasic-description", ""
        )
        all_text = f"{contact_title} {contact_subtitle} {contact_description}"
        return all_text.strip()

    def _process_specific(self, all_text, results):
        """Must be impleted"""
        ia_category = self._process_category(all_text, results)
        results["form-widgets-category"] = ia_category

        ia_facilities = self._process_facilities(all_text, results)
        results["form-widgets-facilities"] = ia_facilities

        # ia_local_category = self._process_local_category(all_text, results)
        # results["form-widgets-local_category"] = ia_local_category
        return results

    def _process_category(self, all_text, results):
        category_voc = self._get_structured_data_from_vocabulary(
            "imio.directory.vocabulary.ContactCategories"
        )
        data = self._ask_categorization_to_ia(all_text, category_voc)
        if not data:
            return
        ia_categories = [
            {"title": r.get("title"), "token": r.get("token")}
            for r in data.get("result", [])
        ]
        return ia_categories

    def _process_facilities(self, all_text, results):
        facilities_voc = self._get_structured_data_from_vocabulary(
            "imio.directory.vocabulary.Facilities", self.context
        )
        data = self._ask_categorization_to_ia(all_text, facilities_voc)
        if not data:
            return
        ia_facilities = [
            {"title": r.get("title"), "token": r.get("token")}
            for r in data.get("result", [])
        ]
        return ia_facilities
