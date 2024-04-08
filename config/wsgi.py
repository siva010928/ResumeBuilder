import os
import sys
import newrelic.agent
from pathlib import Path

from django.core.wsgi import get_wsgi_application
newrelic.agent.initialize('newrelic.ini')
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(BASE_DIR / "app"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_wsgi_application()
application = newrelic.agent.wsgi_application()(application)
