from django import template
from django.utils.safestring import mark_safe
import markdown

register = template.Library()


@register.filter(name='markdown_to_html')
def markdown_to_html(text):
    return mark_safe(
        markdown.markdown(
            text,
            extensions=[
                'fenced_code',
                'codehilite',
                'nl2br',
                'mdx_truly_sane_lists',
                'mdx_breakless_lists',
            ],
            extension_configs={
                'mdx_truly_sane_lists': {
                    'nested_indent': 2,
                    'truly_sane': True,
                }
            },
        )
    )
