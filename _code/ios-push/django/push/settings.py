from django.conf import settings


# IOS keys_file
IOS_KEYS_FILE = getattr(settings, 'PUSH_IOS_KEYS_FILE', 'devpush.pem')
IOS_SANDBOX = getattr(settings, 'PUSH_IOS_SANDBOX', True)
IOS_CLEAN_INTERVAL = getattr(settings, 'PUSH_IOS_CLEAN_INTERVAL', 3600)
