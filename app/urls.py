from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from app import settings

urlpatterns = patterns('',
    url(r'^$', 'home.views.login', name='login'),
    url(r'^home', 'home.views.collection_list', name='list'),
    url(r'^collection/list$', 'home.views.collection_list', name='list'),
    url(r'^collection/new$', 'home.views.collection_edit', name='edit'),
    url(r'^collection/([a-zA-Z0-9\-]+)/delete', 'home.views.collection_delete', name='delete'),
    url(r'^collection/([a-zA-Z0-9\-]+)/edit$', 'home.views.collection_edit', name='edit'),
    url(r'^collection/([a-zA-Z0-9\-]+)$', 'home.views.collection_edit', name='edit'),
    url(r'^settings$', 'home.views.settings', name='settings'),
    url(r'^logout$', 'home.views.logout', name='logout'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
 (r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
 )