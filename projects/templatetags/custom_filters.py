from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """Splits a string by the given argument"""
    if value:
        return value.split(arg)
    return []

@register.filter(name='split_and_strip')
def split_and_strip(value, arg):
    """Splits a string by the given argument and strips whitespace from each item"""
    if value:
        return [item.strip() for item in value.split(arg)]
    return []