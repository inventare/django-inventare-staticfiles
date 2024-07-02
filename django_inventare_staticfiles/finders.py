import json
import tempfile
from typing import Any, List, Optional, Tuple

from django.apps import apps
from django.contrib.staticfiles.finders import BaseFinder
from django.core.checks import Error
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.module_loading import import_string

validate_url = URLValidator()


class RemoteFileInfo:
    """
    A utility class used for store file_name and url and used as wrapper for storage
    in list method of BaseFinder and to download files in find method.
    """

    tag_name: str
    file_name: str
    url: str

    def __init__(self, tag_name: str, file_name: str, url: str):
        self.tag_name = tag_name
        self.file_name = file_name
        self.url = url

    def path(self, value):
        if value != self.file_name:
            return None
        return value

    def download(self):
        import os

        temp_file = os.path.join(
            tempfile.gettempdir(), os.path.basename(self.file_name)
        )

        from urllib.request import urlretrieve

        urlretrieve(self.url, temp_file)

        return temp_file

    def open(self, value):
        if value != self.file_name:
            return None
        temp_file = self.download()
        return open(temp_file)


class RemoteFileFinder(BaseFinder):
    """
    A static files finder that find remote file configuration's across
    your apps, and use this settings to  download the vendor files as
    temporary path's and serve when needed.
    """

    files: List[RemoteFileInfo] = []

    def _get_vendor_modules(self) -> List[Tuple[Any, str]]:
        """
        Load the VENDOR_REMOTE_FILES variable from vendor module in each app
        and return a list of tuples containing the modules and the import string.
        """
        configs = apps.get_app_configs()
        modules = []
        for config in configs:
            import_module = f"{config.name}.vendor.VENDOR_REMOTE_FILES"
            try:
                module = import_string(import_module)
                modules.append((module, import_module))
            except ImportError:
                pass
        return modules

    def _parse_module(self, module):
        for root in module:
            if isinstance(root, (list, tuple)):
                tag_name, file_name, url = root
            elif isinstance(root, dict):
                tag_name = root.get("name")
                file_name = root.get("file_name")
                url = root.get("url")

            self.files.append(RemoteFileInfo(tag_name, file_name, url))

    def _parse_module_list(self):
        if len(self.files) != 0:
            return
        for module, _ in self.modules:
            self._parse_module(module)

    def __init__(self, app_names=None, *args, **kwargs):
        self.files = []
        self.modules = self._get_vendor_modules()

    def list(self, ignore_patterns):
        self._parse_module_list()
        for item in self.files:
            yield item.file_name, item

    def find(self, path, all=False):
        self._parse_module_list()

        files = []
        for item in self.files:
            if item.file_name == path:
                downloaded = item.download()
                if not all:
                    return downloaded
                files.append(downloaded)
        return files

    def _fail(self, error: str, id: str, hint: Optional[str]):
        return [Error(error, hint=hint, id=id)]

    def _check_module(self, module, import_path: str):
        if not isinstance(module, (list, tuple)):
            return self._fail(
                f"{import_path}: is not a tuple or list.",
                hint="Perhaps you forgot a trailing comma?",
                id="django_inventare_staticfiles.E001",
            )
        for root in module:
            if isinstance(root, (list, tuple)):
                root = list(root)
                if len(root) != 3:
                    return self._fail(
                        f"{import_path}: {str(root)} should have exactly three elements.",
                        hint="Perhaps you forgot a trailing comma?",
                        id="django_inventare_staticfiles.E002",
                    )
                tag_name, file_name, url = root
                if not tag_name or not url or not file_name:
                    return self._fail(
                        f"{import_path}: the name, file_name or url is invalid.",
                        hint="Add url and file_name key",
                        id="django_inventare_staticfiles.E005",
                    )
                try:
                    validate_url(url)
                except ValidationError:
                    return self._fail(
                        f"{import_path}: the url is invalid: {url}",
                        hint="Check the url, schemas.",
                        id="django_inventare_staticfiles.E003",
                    )
            elif isinstance(root, dict):
                tag_name = root.get("name")
                url = root.get("url")
                file_name = root.get("file_name")
                if not tag_name or not url or not file_name:
                    return self._fail(
                        f"{import_path}: {json.dumps(root)} should have name, file_name and url keys.",
                        hint="Add url and file_name key",
                        id="django_inventare_staticfiles.E004",
                    )
                try:
                    validate_url(url)
                except ValidationError:
                    return self._fail(
                        f"{import_path}: the url is invalid: {url}",
                        hint="Check the url, schemas.",
                        id="django_inventare_staticfiles.E003",
                    )
            else:
                return self._fail(
                    f"{import_path}: the item has a invalid type.",
                    hint="Should be a list, tuple or dict.",
                    id="django_inventare_staticfiles.E006",
                )
        return []

    def check(self, **kwargs: Any):
        modules = self._get_vendor_modules()
        for module, import_path in modules:
            errors = self._check_module(module, import_path)
            if not errors:
                continue
            return errors
        return []
