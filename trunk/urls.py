from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^ratonator/', include('ratonator.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^/?$', 'ratonator.front.views.index'),
    (r'^action/addSubject$', 'ratonator.front.views.addSubject'),
    (r'^action/logon', 'ratonator.front.views.logon'),
    (r'^action/logoff', 'ratonator.front.views.logoff'),
    (r'^action/language', 'ratonator.front.views.language'),
    (r'^action/search', 'ratonator.front.views.search'),
    (r'^action/register', 'ratonator.front.views.register'),
    (r'^action/(?P<language_code>[a-z]{2})/subject/(?P<subject_name_slugged>[^/]+)/addDefinition', 'ratonator.front.views.addDefinition'),
    (r'^action/(?P<language_code>[a-z]{2})/subject/(?P<subject_name_slugged>[^/]+)/addRate', 'ratonator.front.views.addRate'),
    (r'^action/(?P<language_code>[a-z]{2})/subject/(?P<subject_name_slugged>[^/]+)/addCategory', 'ratonator.front.views.addCategory'),
    (r'^(?P<language_code>[a-z]{2})/subject/(?P<subject_name_slugged>[^/]+)$', 'ratonator.front.views.subject'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^rosetta/',  include('rosetta.urls')), 
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_PATH})
    )
