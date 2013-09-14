__author__ = 'delin'


def modules_urlpattern():
    from django.conf.urls import patterns, url, include
    from django.utils.importlib import import_module
    from MyAdmin.settings import INSTALLED_MODULES

    urlpatterns = []
    for module in INSTALLED_MODULES:
        cur_module = import_module(module).myadmin_module

        urlpatterns += patterns(
            '',
            url(r'^module/' + cur_module.app_name + '/',
                include(module + '.urls', app_name=cur_module.app_name)),
        )

    return urlpatterns