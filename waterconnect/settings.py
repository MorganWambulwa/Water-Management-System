"""
Django settings for waterconnect project.
... (Standard Django comments)
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CORE PROJECT CONFIG ---

# Default settings are for development.
# In production, these should be overridden in a local_settings.py file
# or with environment variables.

# It's recommended to generate a new key for production.
SECRET_KEY = 'a-default-secret-key-that-is-not-secure'

# By default, DEBUG is off.
DEBUG = False

# In production, set this to the domain name of your site.
ALLOWED_HOSTS = []

# --- APPLICATION DEFINITION ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'waterapp', 
]

MIDDLEWARE = [
    # ... (No changes here, standard middleware)
    'django.middleware.security.SecurityMiddleware',
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
        # FIX/UPDATE: Using os.path.join is necessary when working with pathlib (Path) for DIRS path definition outside the project.
        # This ensures the 'templates' folder at the root level (WATER_PROJECT/templates) is found.
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

# --- DATABASE, PASSWORDS, I18N ---
# ... (No changes in these sections)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


LOGIN_REDIRECT_URL = 'dashboard' 

# ADDITION 2: Sets the page users go to after logging out (Index view)
LOGOUT_REDIRECT_URL = 'index'

# --- STATIC FILES ---

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- DEFAULT PRIMARY KEY ---

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- EMAIL CONFIG (FIXED/UPDATED) ---

# FIX/UPDATE: The backend path for email was incorrect. Changed it to standard Django path.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' 
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '' # Set in local_settings.py or environment variables
EMAIL_HOST_PASSWORD = '' # Set in local_settings.py or environment variables

# waterconnect/settings.py

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True
USE_TZ = True

# --- LOCAL SETTINGS ---
# The local_settings.py file is not tracked in git and is used to override
# settings for the local development environment.
try:
    from .local_settings import *
except ImportError:
    pass