from django.template import Library, Node, TemplateSyntaxError
from django.utils import formats

register = Library()


@register.filter(is_safe=False)
def localize(value):
    """
    Force a value to be rendered as a localized value.
    """
    return str(formats.localize(value, use_l10n=True))


@register.filter(is_safe=False)
def unlocalize(value):
    """
    Force a value to be rendered as a non-localized value.
    """
    return str(formats.localize(value, use_l10n=False))


class LocalizeNode(Node):
    def __init__(self, nodelist, use_l10n):
        self.nodelist = nodelist
        self.use_l10n = use_l10n

    def __repr__(self):
        return "<%s>" % self.__class__.__name__

    def render(self, context):
        old_setting = context.use_l10n
        context.use_l10n = self.use_l10n
        output = self.nodelist.render(context)
        context.use_l10n = old_setting
        return output


@register.tag("localize")
def localize_tag(parser, token):
    """
    Force or prevents localization of values.

    Sample usage::

        {% localize off %}
            var pi = {{ 3.1415 }};
        {% endlocalize %}
    """
    bits = token.split_contents()
    bits_len = len(bits)
    if bits_len == 1:
        use_l10n = True
    elif bits_len > 2:
        raise TemplateSyntaxError("%r argument should be 'on' or 'off'" % bits[0])
    else:
        b1 = bits[1]
        # Faster membership check on tuple with only two literals
        if b1 == "on":
            use_l10n = True
        elif b1 == "off":
            use_l10n = False
        else:
            raise TemplateSyntaxError("%r argument should be 'on' or 'off'" % bits[0])
    nodelist = parser.parse(("endlocalize",))
    parser.delete_first_token()
    return LocalizeNode(nodelist, use_l10n)
