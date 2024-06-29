from unittest.mock import MagicMock, patch

from django.test import TestCase

from django_vendor.templatetags.vendor import vendor_remote_url

URL1 = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
MODULE = [
    ["file", "file.js", URL1],
]


class VendorTemplateTagTestCase(TestCase):
    @patch("django_vendor.finders.apps.get_app_configs")
    @patch("django_vendor.finders.import_string")
    def test_call_template_tag(self, mock_import: MagicMock, mock: MagicMock):
        my_app = MagicMock()
        my_app.name = "my_application"
        mock.return_value = [my_app]
        mock_import.return_value = MODULE

        url = vendor_remote_url("file")
        self.assertEqual(url, "/static/file.js")

    @patch("django_vendor.finders.apps.get_app_configs")
    @patch("django_vendor.finders.import_string")
    def test_call_template_tag_invalid(self, mock_import: MagicMock, mock: MagicMock):
        my_app = MagicMock()
        my_app.name = "my_application"
        mock.return_value = [my_app]
        mock_import.return_value = MODULE

        with self.assertRaises(Exception):
            vendor_remote_url("file2")
