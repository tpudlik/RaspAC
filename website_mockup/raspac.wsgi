import sys

activate_this = '/var/www/website/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
sys.path.append('/var/www/website')

from raspac import app as application
