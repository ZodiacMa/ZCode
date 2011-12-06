#coding:utf-8

from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'MySite.views.home', name='home'),
    # url(r'^MySite/', include('MySite.foo.urls')),

    url(r'^my-management/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'^media/(?P<path>.*)$', 'serve', {
            'document_root': settings.MEDIA_ROOT,
            'show_indexes': True,
            }),
    )
