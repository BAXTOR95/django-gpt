from django import template
from django.utils.safestring import mark_safe
import markdown
from markdown.extensions import Extension
from markdown.extensions.codehilite import CodeHiliteExtension

register = template.Library()


class EscapeHtml(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.deregister('html_block')
        md.inlinePatterns.deregister('html')


@register.filter(name='markdown_to_html')
def markdown_to_html(text):
    html = markdown.markdown(
        text,
        extensions=[
            'extra',
            'nl2br',
            EscapeHtml(),
            CodeHiliteExtension(linenums=True, guess_lang=False, css_class='highlight'),
        ],
        output_format='html5',
    )

    # Post-processing to ensure paragraphs have proper spacing
    html = html.replace('<p>', '<p style="margin-bottom: 1em;">')
    return mark_safe(html)
