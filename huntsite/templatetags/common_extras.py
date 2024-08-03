from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
import markdown as md

register = template.Library()


@register.filter
def dictget(dict, key):
    return dict[key]


@register.filter()
def split(value):
    return value.split()


@register.simple_tag()
def markdown(md_path):
    raw_content = (settings.BASE_DIR / "templates" / md_path).read_text()
    return mark_safe(md.markdown(raw_content))
