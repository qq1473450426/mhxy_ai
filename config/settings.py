from pathlib import Path
BASE_DIR=Path(__file__).resolve().parent.parent
SECRET_KEY='local-change-me'
DEBUG=True
ALLOWED_HOSTS=['127.0.0.1','localhost','*']
INSTALLED_APPS=['django.contrib.contenttypes','django.contrib.staticfiles','dashboard']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware']
ROOT_URLCONF='config.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request']}}]
WSGI_APPLICATION='config.wsgi.application'
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'data.sqlite3'}}
LANGUAGE_CODE='zh-hans'; TIME_ZONE='Asia/Shanghai'; USE_I18N=True; USE_TZ=True
STATIC_URL='/static/'; STATICFILES_DIRS=[BASE_DIR/'static']
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
