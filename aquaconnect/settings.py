"""
Django settings for aquaconnect project.
... (Standard Django comments)
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CORE PROJECT CONFIG ---

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1+#8gg=0h2_(8-m2dc8)!+fsbn_1ky1xsawhfj@h9vk##blemn' # Replace this with a secure key in production

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

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

ROOT_URLCONF = 'aquaconnect.urls'

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

WSGI_APPLICATION = 'aquaconnect.wsgi.application'

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
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-email-password'

# aquaconnect/settings.py

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True
USE_TZ = True