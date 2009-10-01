from django.conf.urls.defaults import *

from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^/?$', 'front.views.root'),
    (r'^(?P<language_code>[a-z]{2})$', 'front.views.index'),
    (r'^(?P<language_code>[a-z]{2})/(?P<subject_name_slugged>[^/]+)$', 'front.views.subject'),
    (r'^(?P<language_code>[a-z]{2})/subject/(?P<subject_name_slugged>[^/]+)$', 'front.views.subject_old'),
    (r'^Action/AddSubject$', 'front.views.addSubject'),
    (r'^Action/Logon', 'front.views.logon'),
    (r'^Action/Logoff', 'front.views.logoff'),
    (r'^SetLanguage/(?P<language_code>[a-z]{2})$', 'front.views.language'),
    (r'^Action/Search', 'front.views.search'),
    (r'^Action/Register', 'front.views.register'),
    (r'^Action/Confirm/(?P<key>[0-9a-f-]+)$',  'front.views.registration_validation'), 
    (r'^Action/PasswordReset$',  'front.views.forgot_password'), 
    (r'^Action/PasswordReset/(?P<key>[0-9a-f-]+)$',  'front.views.password_reset'), 
    (r'^Action/(?P<language_code>[a-z]{2})/Subject/(?P<subject_name_slugged>[^/]+)/NewDefinition', 'front.views.addDefinition'),
    (r'^Action/(?P<language_code>[a-z]{2})/Subject/(?P<subject_name_slugged>[^/]+)/NewRate', 'front.views.addRate'),
    (r'^Action/(?P<language_code>[a-z]{2})/Subject/(?P<subject_name_slugged>[^/]+)/NewCategory', 'front.views.addCategory'),
    (r'^Action/(?P<rateable_class>[a-z]+)/(?P<rateable_uuid>[a-f0-9-]+)/NewRate\?placeValuesBeforeTB_=savedValues&TB_iframe=true&height=300&width=400&modal=true',  'front.views.add_rate_with_parameters'), 
    (r'^Action/(?P<rateable_class>[a-z]+)/(?P<rateable_uuid>[a-f0-9-]+)/NewRate',  'front.views.add_rate'), 
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^rosetta/',  include('rosetta.urls')), 
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_PATH})
    )
