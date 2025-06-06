# In your `templatetags` file, e.g., custom_filters.py
from django import template
register = template.Library()

@register.filter
def add(value1, value2):
    return value1 + value2

@register.filter
def multiply(value1, value2):
    return value1 * value2