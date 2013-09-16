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

    url(r'^users/$', 'main.views.page_users', name='users'),
    url(r'^user/add/$', 'main.views.page_user_add', name='user_add'),
    url(r'^user/group/add/$', 'main.views.page_user_group_add', name='user_group_add'),

    url(r'^logs/$', 'main.views.page_logs', name='logs'),
    url(r'^logs/(?P<log_id>\d+)/$', 'main.views.page_log_view', name='log_view'),

    url(r'^about/$', 'main.views.page_about', name='about'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += modules_urlpattern()