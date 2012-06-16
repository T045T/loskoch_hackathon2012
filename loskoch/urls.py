from django.conf import settings
from django.conf.urls import patterns, include, url, static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^facebook/', include('django_facebook.urls')),
    url(r'^accounts/', include('django_facebook.auth_urls')),

    url(r'^admin/', include(admin.site.urls)),

    url('', include('core.urls')),

) + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
