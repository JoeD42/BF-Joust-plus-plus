from django import template

register = template.Library()

@register.filter(name="numspace")
def numspace(num, max_digits):
    return f"{' '*(max_digits-len(str(num)))}{num}"
