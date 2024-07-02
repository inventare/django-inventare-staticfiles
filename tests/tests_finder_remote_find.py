from unittest.mock import MagicMock, patch

from django.test import TestCase

from django_inventare_staticfiles.finders import RemoteFileFinder

URL1 = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
URL2 = "https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.8/dist/umd/popper.min.js"
MODULE = [
    ["file", "file.js", URL1],
    ["file2", "file2.js", URL2],
]


class RemoteFileFinderFindTestCase(TestCase):
    @patch("django_inventare_staticfiles.finders.apps.get_app_configs")
    @patch("django_inventare_staticfiles.finders.import_string")
    @patch("django_inventare_staticfiles.finders.RemoteFileInfo.download")
    def test_find(
        self, mock_download: MagicMock, mock_import: MagicMock, mock: MagicMock
    ):
        my_app = MagicMock()
        my_app.name = "my_application"
        content_value = "my-any-downloaded-file-content"

        mock.return_value = [my_app]
        mock_import.return_value = MODULE
        mock_download.return_value = content_value

        finder = RemoteFileFinder()
        content = finder.find("file.js", all=False)

        self.assertEqual(content, content_value)
        mock_download.assert_called_once()

    @patch("django_inventare_staticfiles.finders.apps.get_app_configs")
    @patch("django_inventare_staticfiles.finders.import_string")
    @patch("django_inventare_staticfiles.finders.RemoteFileInfo.download")
    def test_find_all(
        self, mock_download: MagicMock, mock_import: MagicMock, mock: MagicMock
    ):
        my_app = MagicMock()
        my_app.name = "my_application"
        content_value = "my-any-downloaded-file-content"

        mock.return_value = [my_app]
        mock_import.return_value = MODULE
        mock_download.return_value = content_value

        finder = RemoteFileFinder()
        content = finder.find("file.js", all=True)

        self.assertListEqual(content, [content_value])
        mock_download.assert_called_once()

    @patch("django_inventare_staticfiles.finders.apps.get_app_configs")
    @patch("django_inventare_staticfiles.finders.import_string")
    def test_find_parsed_files_count(self, mock_import: MagicMock, mock: MagicMock):
        my_app = MagicMock()
        my_app.name = "my_application"

        mock.return_value = [my_app]
        mock_import.return_value = MODULE

        finder = RemoteFileFinder()
        finder.find("file.js")
        original_files = len(finder.files)
        finder.find("file.js")
        new_files = len(finder.files)

        self.assertEqual(original_files, new_files)
