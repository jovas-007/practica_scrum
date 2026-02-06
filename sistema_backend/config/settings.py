"""
Django settings for Sistema de Gestión de Tareas
Configurado para TiDB Cloud (producción) y MySQL local (desarrollo)
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-sistema-tareas-buap-2026-dev-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.railway.app', '.onrender.com', '*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'corsheaders',
    'django_filters',
    # Local apps
    'users',
    'tareas',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database - TiDB Cloud (Producción)
import os

# Detectar si estamos en producción o desarrollo
IS_PRODUCTION = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RENDER') or os.environ.get('TIDB_HOST')

if IS_PRODUCTION:
    # TiDB Cloud - Producción
    import ssl
    DATABASES = {
        'default': {
            'ENGINE': 'django_tidb',
            'NAME': os.environ.get('TIDB_DATABASE', 'sistema_tareas'),
            'USER': os.environ.get('TIDB_USER', '37QFcSa1HSQDHNE.root'),
            'PASSWORD': os.environ.get('TIDB_PASSWORD', 'bOvay0l4SI0w3lZA'),
            'HOST': os.environ.get('TIDB_HOST', 'gateway01.us-east-1.prod.aws.tidbcloud.com'),
            'PORT': int(os.environ.get('TIDB_PORT', 4000)),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'ssl': {
                    'ssl_mode': ssl.CERT_REQUIRED,
                },
            },
        }
    }
else:
    # MySQL Local - Desarrollo (XAMPP)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'sistema_tareas',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '3307',
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }
    # PyMySQL ya está configurado en config/__init__.py

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Password hashers - incluir bcrypt para contraseñas migradas de Node.js
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'users.hashers.BcryptPasswordHasher',
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
]

# Internationalization
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Media files (uploads de usuarios)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Límite de archivos: 20MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024  # 20MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024  # 20MB

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}

# CORS - Permitir conexiones desde el frontend Angular
CORS_ALLOW_ALL_ORIGINS = True  # Solo para desarrollo

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-user-id',
]

# Configuración de Email - Django Mail Backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_USER', 'secretaria.instituto.aca@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'ffhd mnft jbnj cglc')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_TIMEOUT = 30
