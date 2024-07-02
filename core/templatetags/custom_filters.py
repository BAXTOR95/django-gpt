import requests
from django import template
from django.conf import settings
from hashlib import md5

register = template.Library()


@register.filter(name='add_class')
def add_class(value, arg):
    css_classes = value.field.widget.attrs.get('class', '')
    value.field.widget.attrs['class'] = f"{css_classes} {arg}"
    return value


@register.filter(name='add_attrs')
def add_attrs(field, css):
    attrs = {}
    definition = css.split(',')
    for d in definition:
        if ':' not in d:
            attrs['class'] = d
        else:
            key, val = d.split(':')
            attrs[key] = val
    return field.as_widget(attrs=attrs)


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


@register.filter(name='unsplash_image')
def unsplash_image(query):
    UNSPLASH_ACCESS_KEY = settings.UNSPLASH_ACCESS_KEY
    url = 'https://api.unsplash.com/photos/random'
    params = {'query': query, 'orientation': 'landscape', 'count': 1}
    headers = {'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'}

    try:
        response = requests.get(url, params=params, headers=headers)
        json_response = response.json()
        if json_response and isinstance(json_response, list) and len(json_response) > 0:
            return json_response[0]['urls']['regular']
    except Exception as e:
        print(f"Error fetching Unsplash image: {e}")

    return None
