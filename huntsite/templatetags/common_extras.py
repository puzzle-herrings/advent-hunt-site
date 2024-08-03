import datetime

from django import template

register = template.Library()


@register.filter
def dictget(dict, key):
    return dict[key]


@register.filter()
def split(value):
    return value.split()


@register.filter()
def mydate(value):
    assert isinstance(value, datetime.datetime), type(value)
    return "foo"
