from .models import Parameter


def add_global_parameter_context(request):
    params = Parameter.objects.filter(is_global=True)
    context = dict()
    for param in params:
        context[param.slug] = param.str()
    return context
