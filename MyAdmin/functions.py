from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.importlib import import_module
from django.utils.translation import ugettext as _
from MyAdmin.settings import APP_CONFIGS, INSTALLED_MODULES
from main.models import Module, Log

__author__ = 'delin'


def prepare_data(request):
    modules_db = Module.objects.filter().all()

    modules = []
    for module in modules_db:
        modules.append({
            'name': module.name,
            'app_name': module.app_name,
            'main_page': reverse("module-" + module.app_name + "_" + module.main_page),
            'author': module.author,
            'author_email': module.author_email,
            'version': module.version,
            'home_page': module.home_page,
            'installed_at': module.installed_at,
            'in_menu': module.in_menu,
            'is_enabled': module.is_enabled,
        })

    data = {
        'app': APP_CONFIGS,
        'modules': modules,
    }

    return data


def modules_update(request):
    installed_modules = Module.objects.values_list('name')
    installed_modules_count = installed_modules.count()

    new_modules = 0
    for module_in_list in INSTALLED_MODULES:
        try:
            module = import_module(module_in_list).myadmin_module

            if installed_modules_count == 0 or module.name not in installed_modules[0]:
                    Module(
                        name=module.name,
                        app_name=module.app_name,
                        version=module.version,
                        author=module.author,
                        author_email=module.author_email,
                        main_page=module.main_page,
                        home_page=module.home_page,
                        description=module.description,
                        in_menu=module.in_menu,
                    ).save()

                    Log(
                        action=0,
                        user=request.user,
                    ).save()

                    new_modules += 1
        except Exception as e:
            messages.error(request, e)

    return new_modules