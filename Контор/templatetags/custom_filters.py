from django import template

register = template.Library()

"""
@register.filter
def get_resident(residents, story_unit):
    # Unpack story and unit from the tuple
    story, unit = story_unit
    # Use a generator expression to find the resident that matches the story and unit
    return next((resident for resident in residents if resident.story == story and resident.unit == unit), None)
"""

register = template.Library()

@register.filter
def range_filter(value):
    return range(1, value + 1)

@register.filter
def get_resident(residents, story_unit):
    story, unit = story_unit  # Unpack the tuple
    return next((resident for resident in residents if resident.story == story and resident.unit == unit), None)




