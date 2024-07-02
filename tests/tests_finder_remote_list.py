from unittest.mock import MagicMock, patch

from django.test import TestCase

from django_inventare_staticfiles.finders import RemoteFileFinder

URL1 = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
URL2 = "https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.8/dist/umd/popper.min.js"
MODULE = [
    ["file", "file.js", URL1],
    {
        "name": "file2",
        "file_name": "file2.js",
        "url": URL2,
    },
]


class RemoteFileFinderListTestCase(TestCase):
    @patch("django_inventare_staticfiles.finders.apps.get_app_configs")
    @patch("django_inventare_staticfiles.finders.import_string")
    def test_initializer(self, mock_import: MagicMock, mock: MagicMock):
        my_app = MagicMock()
        my_app.name = "my_application"
        import_str = f"{my_app.name}.vendor.VENDOR_REMOTE_FILES"

        mock.return_value = [my_app]
        mock_import.return_value = MODULE

        finder = RemoteFileFinder()

        mock_import.assert_called_once_with(import_str)
        self.assertListEqual([(MODULE, import_str)], finder.modules)

    @patch("django_inventare_staticfiles.finders.apps.get_app_configs")
    @patch("django_inventare_staticfiles.finders.import_string")
    def test_list(self, mock_import: MagicMock, mock: MagicMock):
        my_app = MagicMock()
        my_app.name = "my_application"

        mock.return_value = [my_app]
        mock_import.return_value = MODULE

        finder = RemoteFileFinder()
        paths = list(finder.list([]))
        self.assertEqual(len(paths), 2)
        item1, item2 = paths

        self.assertEqual(item1[0], "file.js")
        self.assertEqual(item1[1].url, URL1)

        self.assertEqual(item2[0], "file2.js")
        self.assertEqual(item2[1].url, URL2)

    @patch("django_inventare_staticfiles.finders.apps.get_app_configs")
    @patch("django_inventare_staticfiles.finders.import_string")
    def test_list_parsed_files_count(self, mock_import: MagicMock, mock: MagicMock):
        my_app = MagicMock()
        my_app.name = "my_application"

        mock.return_value = [my_app]
        mock_import.return_value = MODULE

        finder = RemoteFileFinder()
        list(finder.list([]))
        original_files = len(finder.files)
        list(finder.list([]))
        new_files = len(finder.files)

        self.assertEqual(original_files, new_files)
