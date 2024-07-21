from django import template

register = template.Library()


@register.filter
def dictget(dict, key):
    return dict[key]
