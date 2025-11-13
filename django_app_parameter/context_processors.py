from .models import Parameter


def add_global_parameter_context(request):
    return {
        param.slug: param.str() for param in Parameter.objects.filter(is_global=True)
    }
