from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from modules import modules_urlpattern

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'main.views.page_home', name='home'),

    url(r'^login/$', 'main.views.page_login', name='login'),
    url(r'^logout/$', 'main.views.page_logout', name='logout'),

    url(r'^modules/$', 'main.views.page_modules', name='modules'),
    url(r'^logs/$', 'main.views.page_logs', name='logs'),
    url(r'^about/$', 'main.views.page_about', name='about'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += modules_urlpattern()