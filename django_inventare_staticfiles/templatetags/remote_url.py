from django.template import Library
from django.templatetags.static import static
from django_vendor.finders import RemoteFileFinder

register = Library()


@register.simple_tag
def remote_url(name: str):
    finder = RemoteFileFinder()
    finder._parse_module_list()
    for file in finder.files:
        if file.tag_name == name:
            return static(file.file_name)
    raise Exception(f"Unknown vendor remote url file: {name}")
