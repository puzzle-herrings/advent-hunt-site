import datetime

from django import template

register = template.Library()


@register.filter
def dictget(dict, key):
    return dict[key]


@register.filter()
def split(value):
    return value.split()
