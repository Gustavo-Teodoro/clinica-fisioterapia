from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ── SEGURANÇA ────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-clinica-fernanda-teodoro-2026'
)
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    'gustavoteodoro.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]

# ── APPS ─────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'clinica.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'staticfiles'],
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': ['django.template.context_processors.request']},
    },
]

WSGI_APPLICATION = 'clinica.wsgi.application'

# ── BANCO DE DADOS ───────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'clinica.db',
    }
}

# ── IDIOMA E FUSO ────────────────────────────────────────────────────────
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = False

# ── ARQUIVOS ESTÁTICOS ───────────────────────────────────────────────────
STATIC_URL = '/assets/'
STATICFILES_DIRS = [BASE_DIR / 'staticfiles' / 'assets']
STATIC_ROOT = BASE_DIR / 'static_root'
WHITENOISE_ROOT = BASE_DIR / 'staticfiles'

# ── MEDIA (uploads de exames PDF) ────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── REST FRAMEWORK ───────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'UNAUTHENTICATED_USER': None,
    'DATE_FORMAT': '%Y-%m-%d',
    'DATE_INPUT_FORMATS': ['%Y-%m-%d'],
}

# ── CORS ─────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    'https://gustavoteodoro.pythonanywhere.com',
]
CORS_ALLOW_ALL_ORIGINS = False

# ── ANTHROPIC (Importar ficha com IA) ────────────────────────────────────
# Defina sua chave em: https://console.anthropic.com/
# Recomendado: use variável de ambiente no servidor
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
