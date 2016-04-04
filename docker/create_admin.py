#!/usr/bin/env python
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pypolo.settings")
from django.contrib.auth.models import User

username = os.environ.get("PYTRADER_USER", 'trader')
password = os.environ.get("PYTRADER_PASSWORD", 'trader')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, '', password)
