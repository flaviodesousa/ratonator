SECRET_KEY = 'obzjpxgua$s5@bksmr&2+*0ze2w07d&s6&2o0*%)u^3bf8z(w@'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_PASSWORD = '{pwemail}'
EMAIL_HOST_USER = 'mailer@ratonator.com'
EMAIL_SUBJECT_PREFIX = '[ratonator.com] '
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = 'mailer@ratonator.com'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

ADMINS = (
    ('Ratonator Admins', 'admins@ratonator.com'),
)

MANAGERS = ADMINS

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'ratonator',
    'USER': 'ratonator_admin',
    'PASSWORD': '{pwdb}',
    'HOST': 'localhost'
  }
}

DEBUG = True