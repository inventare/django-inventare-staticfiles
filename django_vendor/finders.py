import json
import tempfile
from typing import Any, Optional
from django.apps import apps
from django.core.checks import Error
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.contrib.staticfiles.finders import BaseFinder
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
    
    def __repr__(self) -> str:
        return f"<{self.file_name}:{self.url}>"
    
    def path(self, value):
        if value != self.file_name:
            return None
        return value
    
    def download(self):
        import os
        temp_file = os.path.join(tempfile.gettempdir(), os.path.basename(self.file_name))
        
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
    A static files finder that uses the ``REMOTE_STATICFILES`` setting
    to locale and download remote static files.
    """
    files: list[RemoteFileInfo] = []
    
    def get_vendor_modules(self):
        configs = apps.get_app_configs()
        modules = []
        for config in configs:
            import_module = f"{config.name}.vendor.VENDOR_FILES"
            try:
                module = import_string(import_module)
                modules.append(module)
            except ImportError:
                pass
        return modules
    
    def parse_module(self, module):
        for root in module:
            if isinstance(root, (list, tuple)):
                tag_name, file_name, url = root
            elif isinstance(root, dict):
                tag_name = root.get('name')
                file_name = root.get('file_name')
                url = root.get('url')
            
            self.files.append(RemoteFileInfo(tag_name, file_name, url))

    def parse_module_list(self):
        for module in self.modules:
            self.parse_module(module)

    def __init__(self, app_names=None, *args, **kwargs):
        self.files = []
        self.modules = self.get_vendor_modules()

    def list(self, ignore_patterns):
        self.parse_module_list()
        for item in self.files:
            yield item.file_name, item
    
    def find(self, path, all=False):
        self.parse_module_list()

        files = []
        for item in self.files:
            if item.file_name == path:
                downloaded = item.download()
                if not all:
                    return downloaded
                files.append(downloaded)
        return files

    def fail(self, error: str, id: str, hint: Optional[str]):
        return [Error(error, hint=hint, id=id)]
    
    def check_module(self, module):
        if not isinstance(module, (list, tuple)):
            return self.fail(
                "The REMOTE_STATICFILES setting is not a tuple or list.",
                hint="Perhaps you forgot a trailing comma?",
                id="django_vendor.E001",
            )
        for root in module:
            if isinstance(root, (list, tuple)):
                root = list(root)
                if len(root) != 3:
                    return self.fail(
                        f"The REMOTE_STATICFILES item: [{','.join(root)}] as list or tuple should have exactly three elements.",
                        hint="Perhaps you forgot a trailing comma?",
                        id="django_vendor.E002",
                    )
                tag_name, file_name, url = root
                if not tag_name or not url or not file_name:
                    return self.fail(
                        f"The REMOTE_STATICFILES item: [{','.join(root)}] file_name or url is invalid.",
                        hint="Add url and file_name key",
                        id="django_vendor.E005",
                    )
                try:
                    validate_url(url)
                except ValidationError:
                    return self.fail(
                        f"The url is invalid for REMOTE_STATICFILES: {url}.",
                        hint="Check the url, schemas.",
                        id="django_vendor.E003",
                    )
            elif isinstance(root, dict):
                tag_name = root.get('name')
                url = root.get('url')
                file_name = root.get('file_name')
                if not tag_name or not url or not file_name:
                    return self.fail(
                        f"The REMOTE_STATICFILES item: {json.dumps(root)} as dict should have file_name and url keys.",
                        hint="Add url and file_name key",
                        id="django_vendor.E004",
                    )
                try:
                    validate_url(url)
                except ValidationError:
                    return self.fail(
                        f"The url is invalid for REMOTE_STATICFILES: {url}.",
                        hint="Check the url, schemas.",
                        id="django_vendor.E003",
                    )
            else:
                return self.fail(
                    f"The REMOTE_STATICFILES item: {root} has invalid type.",
                    hint="Should be a list, tuple or dict.",
                    id="django_vendor.E006",
                )
        return []

    def check(self, **kwargs: Any):
        modules = self.get_vendor_modules()
        for module in modules:
            errors = self.check_module(module)
            if not errors:
                continue
            return errors
        return []
