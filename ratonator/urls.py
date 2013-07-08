from django.conf.urls import *

from django.conf import settings
from django.contrib import admin

import ratonator

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^/?$', 'front.views.root'),
    (r'^(?P<language_code>[a-z]{2})$', 'front.views.index'),
    (r'^(?P<language_code>[a-z]{2})/(?P<subject_name_slugged>[^/]+)$', 'front.views.subject'),
    (r'^(?P<language_code>[a-z]{2})/subject/(?P<subject_name_slugged>[^/]+)$', 'front.views.subject_old'), # deprecated, permanent
    (r'^(?P<rateable_uuid>[a-f0-9-]+)/rates',  'front.views.rates'), 
    (r'^User/(?P<username>[^/]+)$',  'front.views.user'), 
    (r'^SetLanguage/(?P<language_code>[a-z]{2})$', 'front.views.language'), # deprecated, permanent
    (r'^Action/AddSubject$', 'front.views.addSubject'),
    (r'^Action/(?P<scope>[^/]+)/UserProfile',  'front.views.user_profile'), 
    (r'^Action/Logon', 'front.views.logon'),
    (r'^Action/Logoff', 'front.views.logoff'),
    (r'^Action/Search', 'front.views.search'),
    (r'^Action/Register', 'front.views.register'),
    (r'^Action/Confirm/(?P<key>[0-9a-f-]+)$',  'front.views.registration_validation'), 
    (r'^Action/PasswordReset$',  'front.views.forgot_password'), 
    (r'^Action/PasswordReset/(?P<key>[0-9a-f-]+)$',  'front.views.password_reset'), 
    (r'^Action/(?P<rateable_uuid>[a-f0-9-]+)/NewDefinition', 'front.views.addDefinition'),
    (r'^Action/(?P<rateable_uuid>[a-f0-9-]+)/NewCategory', 'front.views.addCategory'),
    (r'^Action/(?P<rateable_uuid>[a-f0-9-]+)/NewRate\?placeValuesBeforeTB_=savedValues&TB_iframe=true&height=400&width=500&modal=true',  'front.views.add_rate_with_parameters'), 
    (r'^Action/(?P<rateable_uuid>[a-f0-9-]+)/NewRate',  'front.views.add_rate'), 
)

if ratonator.settings.DEBUG:
    urlpatterns += patterns('',
        (r'^rosetta/',  include('rosetta.urls')), 
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': ratonator.settings.STATIC_ROOT})
    )
