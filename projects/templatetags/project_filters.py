# projects/templatetags/project_filters.py
from django import template

register = template.Library()

@register.filter
def split(value, key):
    """
    Returns the value turned into a list.
    """
    try:
        return value.split(key)
    except (AttributeError, ValueError):
        return [value]

@register.filter
def strip(value):
    """
    Strips whitespace from a string
    """
    try:
        return value.strip()
    except AttributeError:
        return value