from MyAdmin.settings import APP_CONFIGS
from main.models import Module

__author__ = 'delin'


def prepare_data(request):
    modules = Module.objects.filter(is_removed=False).all()

    data = {
        'app': APP_CONFIGS,
        'modules': modules,
    }

    return data