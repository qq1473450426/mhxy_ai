import os,sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
from django.core.management import execute_from_command_line
execute_from_command_line([sys.argv[0],'runserver','127.0.0.1:8000'])
