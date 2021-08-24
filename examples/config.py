import os

class Config(object):
    OFSC_CLIENT_ID = os.environ.get('OFSC_CLIENT_ID') or '__token__'
    OFSC_CLIENT_SECRET = os.environ.get('OFSC_CLIENT_SECRET') or '__your_secret_goes_here_'
    OFSC_COMPANY = os.environ.get('OFSC_COMPANY') or 'sunrise'
    OFSC_ROOT = os.environ.get('OFSC_ROOT') or '' # Resource root external name
    OFSC_BASE_URL = os.environ.get('OFSC_BASE_URL') or "https://{}.etadirect.com".format(OFSC_COMPANY)
