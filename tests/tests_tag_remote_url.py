from unittest.mock import MagicMock, patch

from django.template import engines
from django.test import TestCase

from django_inventare_staticfiles.templatetags.remote_url import remote_url

URL1 = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
MODULE = [
    ["file", "file.js", URL1],
]

TEMPLATE_CODE_1 = """
{% load remote_url %}
{% remote_url 'file' %}
"""

TEMPLATE_CODE_2 = """
{% load remote_url %}
{% remote_url 'file2' %}
"""


class VendorTemplateTagTestCase(TestCase):
    @patch("django_vendor.finders.apps.get_app_configs")
    @patch("django_vendor.finders.import_string")
    def test_call_template_tag(self, mock_import: MagicMock, mock: MagicMock):
        my_app = MagicMock()
        my_app.name = "my_application"
        mock.return_value = [my_app]
        mock_import.return_value = MODULE

        url = remote_url("file")
        self.assertEqual(url, "/static/file.js")

    @patch("django_vendor.finders.apps.get_app_configs")
    @patch("django_vendor.finders.import_string")
    def test_call_template_tag_invalid(self, mock_import: MagicMock, mock: MagicMock):
        my_app = MagicMock()
        my_app.name = "my_application"
        mock.return_value = [my_app]
        mock_import.return_value = MODULE

        with self.assertRaises(Exception):
            remote_url("file2")

    @patch("django_vendor.finders.apps.get_app_configs")
    @patch("django_vendor.finders.import_string")
    def test_template_tag_rendered(self, mock_import: MagicMock, mock: MagicMock):
        my_app = MagicMock()
        my_app.name = "my_application"
        mock.return_value = [my_app]
        mock_import.return_value = MODULE

        template = None
        loaded_engines = engines.all()
        for engine in loaded_engines:
            template = engine.from_string(TEMPLATE_CODE_1)

        output = template.render(context={})
        self.assertTrue("/static/file.js" in output)

    @patch("django_vendor.finders.apps.get_app_configs")
    @patch("django_vendor.finders.import_string")
    def test_exception_in_template_tag_rendered(
        self, mock_import: MagicMock, mock: MagicMock
    ):
        my_app = MagicMock()
        my_app.name = "my_application"
        mock.return_value = [my_app]
        mock_import.return_value = MODULE

        template = None
        loaded_engines = engines.all()
        for engine in loaded_engines:
            template = engine.from_string(TEMPLATE_CODE_2)

        with self.assertRaises(Exception):
            template.render(context={})
