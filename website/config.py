# Constants used by raspac.py
# ---------------------------

# Path to command history database
DATABASE = '/var/www/website/raspac.db'

# Debug mode: should be set to False for deployment!
DEBUG = False

# ???  Look up Flask tutorial for documentation
SECRET_KEY = 'mistyczneabecadlo'

# Recognized usernames
USERNAMES = ['Ted', 'MB', 'Thais', 'John']

# Password (the same for all users)
PASSWORD = 'oodlesofdoodles'

# List of supported AC modes
ACMODES = ['off', 'heat', 'cool']

# List of supported AC temperatures
ACTEMPERATURES = map(str, range(64, 87, 2))

