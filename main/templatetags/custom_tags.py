from django import template

register = template.Library()

@register.filter
def range_list(value):
    return range(value)

@register.filter
def index(List, i):
    try:
        return List[int(i)]
    except:
        return None