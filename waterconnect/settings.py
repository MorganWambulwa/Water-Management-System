"""
Django settings for waterconnect project.
"""

from pathlib import Path
import os
import dj_database_url  # type: ignore

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key-change-me')


INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'waterapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'waterconnect.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'waterconnect.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'),
        conn_max_age=600
    )
}


LOGIN_REDIRECT_URL = 'index' 
LOGOUT_REDIRECT_URL = 'index'
LOGIN_URL = 'login'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

JAZZMIN_SETTINGS = {
    "site_url": "/",
    # "site_brand": "WaterConnect Administration",
    # "site_logo": "waterapp/images/favicon.png",
    # "site_title": "WaterConnect",
    # "site_header": "WaterConnect",
    # "site_logo": "waterapp/images/favicon.png",
    "login_logo": None,
    "welcome_sign": "Welcome to the Water System Administration",

    "order_with_respect_to": ["waterapp", "auth"], 
    # "copyright": "WaterConnect © 2025", 
    "custom_css": "waterapp/css/admin_custom.css",
    "search_model": "waterapp.WaterSource",
    "show_ui_builder": False,
    "show_version": False,
    "hide_apps": [],
    "user_avatar": None,
    "show_sidebar": True,
    "actions_sticky": False,
}

# JAZZMIN_UI_TWEAKS = {
#     "theme": "darkly",
#     "dark_mode_theme": "darkly", 
#     "accent": "accent-primary",
#     "navbar_fixed": True,
#     "sidebar_fixed": True,
#     "sidebar": "sidebar-dark-primary",
#     "navbar": "navbar-dark",
#     "sidebar_nav_flat_style": True, 
#     "button_classes": {
#         "primary": "btn-primary",
#         "secondary": "btn-outline-secondary",
#     },
#     "actions_sticky": True,
    
#     # Text sizing flags set to False ensures default readable font size
#     "navbar_small_text": False,
#     "footer_small_text": False,
#     "body_small_text": False,
# }


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' 
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 2525
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER') 
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD') 

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS = [RENDER_EXTERNAL_HOSTNAME]
    DEBUG = False
else:
    ALLOWED_HOSTS = []
    DEBUG = True