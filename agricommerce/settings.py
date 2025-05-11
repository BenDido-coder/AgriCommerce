import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: Keep secret keys in environment variables for production!
SECRET_KEY = 'django-insecure-03yxt(kwu%2)jmqm&((8cm)ghvjn1=tzb#v+4ex3*6v%ct%7da'

# Development mode
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
# For production, consider using: ALLOWED_HOSTS = ['yourdomain.com']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'ac',  # Your custom app
    # Optional: use this instead if needed: 'ac.apps.AcConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'ac.middleware.TransactionAccessMiddleware',  # Custom middleware
]

ROOT_URLCONF = 'agricommerce.urls'

AUTH_USER_MODEL = 'ac.User'

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

WSGI_APPLICATION = 'agricommerce.wsgi.application'

# Database settings (MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'agricommerce',
        'USER': 'Group1',
        'PASSWORD': '02062814#afihimz',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_ALL_TABLES'",
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 300,
    }
}

# Logging (mostly useful for development and debugging DB queries)
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}

# Authentication
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'ac.backends.EmailOrPhoneBackend',  # Your custom backend
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'my_account'
LOGOUT_REDIRECT_URL = 'home'



# Session and CSRF cookies
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_COOKIE_SECURE = True  # Use HTTPS in production
CSRF_COOKIE_SECURE = True     # Use HTTPS in production

# Optional: brute-force protection
RATELIMIT_LOGIN = '5/m'  # Requires django-ratelimit

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'ac/static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Auto Field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Development placeholder
DEBUG_PHONE_NUMBER = '+251900000000'

########### note ##################
#superuser admin information
#"username: Group1
#phone: +251915451380
#email: group1@agri.com
#password: 02062814#afihimz
# This is the superuser account for the admin panel.
###############################
