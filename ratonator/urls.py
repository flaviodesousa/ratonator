from django.conf.urls import *

from django.conf import settings
from django.contrib import admin

import ratonator

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^/?$', 'ratonator.front.views.root'),
    (r'^(?P<language_code>[a-z]{2})$', 'ratonator.front.views.index'),
    (r'^(?P<language_code>[a-z]{2})/(?P<subject_name_slugged>[^/]+)$', 'ratonator.front.views.subject'),
    (r'^(?P<language_code>[a-z]{2})/subject/(?P<subject_name_slugged>[^/]+)$', 'ratonator.front.views.subject_old'), # deprecated, permanent
    (r'^(?P<rateable_uuid>[a-f0-9-]+)/rates',  'ratonator.front.views.rates'), 
    (r'^User/(?P<username>[^/]+)$',  'ratonator.front.views.user'), 
    (r'^SetLanguage/(?P<language_code>[a-z]{2})$', 'ratonator.front.views.language'), # deprecated, permanent
    (r'^Action/AddSubject$', 'ratonator.front.views.addSubject'),
    (r'^Action/(?P<scope>[^/]+)/UserProfile',  'ratonator.front.views.user_profile'), 
    (r'^Action/Logon', 'ratonator.front.views.logon'),
    (r'^Action/Logoff', 'ratonator.front.views.logoff'),
    (r'^Action/Search', 'ratonator.front.views.search'),
    (r'^Action/Register', 'ratonator.front.views.register'),
    (r'^Action/Confirm/(?P<key>[0-9a-f-]+)$',  'ratonator.front.views.registration_validation'), 
    (r'^Action/PasswordReset$',  'ratonator.front.views.forgot_password'), 
    (r'^Action/PasswordReset/(?P<key>[0-9a-f-]+)$',  'ratonator.front.views.password_reset'), 
    (r'^Action/(?P<rateable_uuid>[a-f0-9-]+)/NewDefinition', 'ratonator.front.views.addDefinition'),
    (r'^Action/(?P<rateable_uuid>[a-f0-9-]+)/NewCategory', 'ratonator.front.views.addCategory'),
    (r'^Action/(?P<rateable_uuid>[a-f0-9-]+)/NewRate\?placeValuesBeforeTB_=savedValues&TB_iframe=true&height=400&width=500&modal=true',  'ratonator.front.views.add_rate_with_parameters'), 
    (r'^Action/(?P<rateable_uuid>[a-f0-9-]+)/NewRate',  'ratonator.front.views.add_rate'), 
)

if ratonator.settings.DEBUG:
    urlpatterns += patterns('',
        (r'^rosetta/',  include('rosetta.urls')), 
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': ratonator.settings.STATIC_ROOT})
    )
