# ratonator settings

STATIC_PATH = '/var/www/rate228/app/ratonator/static'
ACCOUNT_VALIDATION_EXPIRATION_DAYS = 5
PASSWORD_RESET_EXPIRATION_DAYS = 3

# Django settings for ratonator project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DEFAULT_FROM_EMAIL = 'mailer@ratonator.com'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

ADMINS = (
    ('Flavio de Sousa', 'flavio@ratonator.com'),
    ('Flavio de Sousa',  'flavio@moonlighting.com.br')
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_NAME = 'ratonator'
DATABASE_USER = 'ratonator_admin'
DATABASE_PASSWORD = 'piconano2'
#DATABASE_PASSWORD = 'pico2.0.7nanopgratadmin'
DATABASE_HOST = 'localhost'
DATABASE_PORT = ''

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_PASSWORD = 'rJ[3/0#Op3/-i?|wg'
EMAIL_HOST_USER = 'mailer@ratonator.com'
EMAIL_SUBJECT_PREFIX = '[ratonator.com] '
EMAIL_USE_TLS = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
RATONATOR_DEFAULT_LANGUAGE = 'en'
LANGUAGE_CODE = 'en-us'
LANGUAGE_COOKIE_NAME = 'language.ratonator.com'
LANGUAGES = (
  ('ar',  ('Arabic')), 
  ('de',  ('German')), 
  ('en', ('English')),
  ('es',  ('Spanish')),
  ('fr',  ('French')), 
  ('he',  ('Hebrew')), 
  ('it',  ('Italian')), 
  ('ja',  ('Japanese')), 
  ('ko',  ('Korean')), 
  ('pl',  ('Polish')), 
  ('pt', ('Portuguese')),
  ('ru',  ('Russian')), 
  ('zh',  ('Chinese')), 
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'obzjpxgua$s5@bksmr&2+*0ze2w07d&s6&2o0*%)u^3bf8z(w@'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    # 'django.template.loaders.eggs.load_template_source',
)

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

MIDDLEWARE_CLASSES = (
    'django.contrib.csrf.middleware.CsrfMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
)

ROOT_URLCONF = 'ratonator.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/var/www/rate228/app/ratonator/templates'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'ratonator.front', 
    'rosetta'
)

AUTH_PROFILE_MODULE = 'front.RateableUser'