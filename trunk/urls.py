from django.conf.urls.defaults import *

from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^/?$', 'front.views.index'),
    (r'^action/addSubject$', 'front.views.addSubject'),
    (r'^action/logon', 'front.views.logon'),
    (r'^action/logoff', 'front.views.logoff'),
    (r'^action/language/(?P<language_code>[a-z]{2})', 'front.views.language'),
    (r'^action/search', 'front.views.search'),
    (r'^action/register', 'front.views.register'),
    (r'^action/(?P<language_code>[a-z]{2})/subject/(?P<subject_name_slugged>[^/]+)/addDefinition', 'front.views.addDefinition'),
    (r'^action/(?P<language_code>[a-z]{2})/subject/(?P<subject_name_slugged>[^/]+)/addRate', 'front.views.addRate'),
    (r'^action/(?P<language_code>[a-z]{2})/subject/(?P<subject_name_slugged>[^/]+)/addCategory', 'front.views.addCategory'),
    (r'^(?P<language_code>[a-z]{2})/subject/(?P<subject_name_slugged>[^/]+)$', 'front.views.subject'),
    (r'^action/(?P<rateable_class>[a-z]+)/(?P<rateable_uuid>[a-f0-9-]+)/addRate\?placeValuesBeforeTB_=savedValues&TB_iframe=true&height=300&width=400&modal=true',  'front.views.add_rate_with_parameters'), 
    (r'^action/(?P<rateable_class>[a-z]+)/(?P<rateable_uuid>[a-f0-9-]+)/addRate',  'front.views.add_rate'), 
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^rosetta/',  include('rosetta.urls')), 
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_PATH})
    )
