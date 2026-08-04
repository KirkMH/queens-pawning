from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from num2words import num2words

register = template.Library()


@register.filter
def field_type(bound_field):
    return bound_field.field.widget.__class__.__name__


@register.filter
def input_class(bound_field):
    widget_class = bound_field.field.widget.attrs.get('class', '')
    css_class = ''
    if bound_field.form.is_bound:
        if bound_field.errors:
            css_class = 'is-invalid'
        elif field_type(bound_field) != 'PasswordInput':
            css_class = 'is-valid'
    return 'form-control {} {}'.format(widget_class, css_class).strip()


@register.filter
def peso(amount):
    return '₱ ' + currency(amount)


@register.filter
def seq_num(number):
    if number:
        return "%06d" % number
    else:
        return ""


@register.filter
def percentage(value):
    if value:
        return f'{value} %'
    else:
        return "0 %"


@register.filter
def currency(amount):
    if amount:
        amount = round(float(amount), 2)
        return "%s%s" % (intcomma(int(amount)), ("%0.2f" % amount)[-3:])
    else:
        return "0.00"


@register.filter
def to_words(value):
    try:
        return num2words(int(value))
    except (ValueError, TypeError):
        return value