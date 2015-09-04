from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from app import settings

urlpatterns = patterns('',
    url(r'^$', 'home.views.login', name='login'),
    url(r'^home$', 'home.views.home', name='home'),
    url(r'^settings', 'home.views.settings', name='settings'),
    url(r'^logout$', 'home.views.logout', name='logout'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
 (r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
 )