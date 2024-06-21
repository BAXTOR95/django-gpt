from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(value, arg):
    css_classes = value.field.widget.attrs.get('class', '')
    value.field.widget.attrs['class'] = f"{css_classes} {arg}"
    return value
