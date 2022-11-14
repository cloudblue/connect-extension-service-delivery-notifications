from jinja2 import BaseLoader, Environment, select_autoescape, TemplateSyntaxError

JINJA_ENV = Environment(
    loader=BaseLoader,
    autoescape=select_autoescape(),
)


def render(template_source, request):
    template = JINJA_ENV.from_string(template_source)
    return template.render(request=request)


def validate(template_source):
    try:
        JINJA_ENV.from_string(template_source)
        return True
    except TemplateSyntaxError:
        return False
