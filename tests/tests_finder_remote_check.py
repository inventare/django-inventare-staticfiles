from unittest.mock import MagicMock, patch

from django.test import TestCase

from django_inventare_staticfiles.finders import RemoteFileFinder

ERROR_MODULES = [
    # NOT NAME
    [
        (
            "",
            "file.js",
            "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
        ),
    ],
    # NOT PATH NAME
    [
        (
            "file",
            "",
            "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
        ),
    ],
    # NOT URL
    [
        ("file", "file.js", ""),
    ],
    # INVALID URL SCHEMA
    [
        (
            "file",
            "file.js",
            "xhttps://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
        ),
    ],
    # MORE THAN THREE ITENS
    [
        (
            "file",
            "file.js",
            "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
            "",
        ),
    ],
    # LESS THAN THREE ITENS
    [
        ("file", "file.js"),
    ],
    # ALL ABOVE, BUT WITH LIST
    [
        [
            "",
            "file.js",
            "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
        ],
    ],
    [
        [
            "file",
            "",
            "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
        ],
    ],
    [
        ["file", "file.js", ""],
    ],
    [
        [
            "file",
            "file.js",
            "xhttps://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
        ],
    ],
    [
        [
            "file",
            "file.js",
            "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
            "",
        ],
    ],
    [
        ["file", "file.js"],
    ],
    # ALL ABOVE, BUT WITH DICT
    [
        {
            "name": "",
            "file_name": "file.js",
            "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
        },
    ],
    [
        {
            "name": "file",
            "file_name": "",
            "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
        },
    ],
    [
        {"name": "file", "file_name": "file.js", "url": ""},
    ],
    [
        {
            "name": "file",
            "file_name": "file.js",
            "url": "xhttps://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
        },
    ],
    # NOT LIST, TUPLE, OR DICT
    [
        MagicMock(),
    ],
]

SUCCESS_MODULES = [
    [
        [
            "file",
            "file.js",
            "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
        ],
    ],
    [
        {
            "name": "file",
            "file_name": "file.js",
            "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
        },
    ],
]


class RemoteFileFinderCheckTestCase(TestCase):
    IMPORT_STR = "@import_str_val@"

    @patch("django_inventare_staticfiles.finders.RemoteFileFinder._get_vendor_modules")
    def test_check_not_list_or_tuple(self, mock: MagicMock):
        mock.return_value = [({}, self.IMPORT_STR)]

        finder = RemoteFileFinder()
        errors = finder.check()
        self.assertEqual(1, len(errors))

    @patch("django_inventare_staticfiles.finders.RemoteFileFinder._get_vendor_modules")
    def test_check_with_errors(self, mock: MagicMock):
        for item in ERROR_MODULES:
            mock.return_value = [(item, self.IMPORT_STR)]

            finder = RemoteFileFinder()
            errors = finder.check()
            self.assertEqual(1, len(errors))

            item = errors[0]
            self.assertTrue(self.IMPORT_STR in item.msg)

    @patch("django_inventare_staticfiles.finders.RemoteFileFinder._get_vendor_modules")
    def test_check_with_success(self, mock: MagicMock):
        for item in SUCCESS_MODULES:
            mock.return_value = [(item, self.IMPORT_STR)]

            finder = RemoteFileFinder()
            errors = finder.check()
            self.assertEqual(0, len(errors))
