import django
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from app import settings
from home import views

urlpatterns = patterns('',
    url(r'^$', views.login, name='login'),
    url(r'^home', views.collection_list, name='list'),
    url(r'^collection/list$', views.collection_list, name='list'),
    url(r'^collection/new$', views.collection_edit, name='edit'),
    url(r'^collection/([a-zA-Z0-9\-]+)/delete', views.collection_delete, name='delete'),
    url(r'^collection/([a-zA-Z0-9\-]+)/edit$', views.collection_edit, name='edit'),
    url(r'^collection/([a-zA-Z0-9\-]+)/process', views.collection_process, name='process'),
    url(r'^collection/([a-zA-Z0-9\-]+)$', views.collection_edit, name='edit'),
    url(r'^settings$', views.settings_page, name='settings'),
    url(r'^logout$', views.logout, name='logout'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
 (r'^static/(.*)$', django.views.static.serve, {'document_root': settings.STATIC_ROOT}),
 )