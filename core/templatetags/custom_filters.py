from django import template
from hashlib import md5

register = template.Library()


@register.filter(name='add_class')
def add_class(value, arg):
    css_classes = value.field.widget.attrs.get('class', '')
    value.field.widget.attrs['class'] = f"{css_classes} {arg}"
    return value


@register.filter(name='gravatar_url')
def gravatar_url(email, size=100, rating='g', default='retro', force_default=False):
    """Generates a gravatar URL for a given email.
    Args:
        email (str): The user's email address.
        size (int): Size of the gravatar image.
        rating (str): Rating of the gravatar image.
        default (str): Default gravatar image style.
        force_default (bool): Whether to force the default image or not.
    Returns:
        str: The gravatar URL.
    """
    hash_value = md5(email.lower().encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{hash_value}?s={size}&d={default}&r={rating}&f={force_default}"
