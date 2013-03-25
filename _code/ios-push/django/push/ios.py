import os.path as op

from apns import APNs, Payload

from .settings import IOS_KEYS_FILE, IOS_SANDBOX


KEYS_DIR = op.abspath(op.join(op.dirname(__file__), 'keys'))
KEYS_FILE = op.join(KEYS_DIR, IOS_KEYS_FILE)

assert op.exists(KEYS_FILE)


def get_server(use_sandbox=IOS_SANDBOX, keys_file=KEYS_FILE):
    " Create and return production or develop server. "
    return APNs(use_sandbox=use_sandbox, cert_file=keys_file, key_file=keys_file)


def send_notify(token, server=None, **payloads):
    " Send simple device notify. "
    server = server or get_server()
    return server.gateway_server.send_notification(token, Payload(**payloads))


def get_feedbacks(server=None):
    " Get inactive tokens. "
    server = server or get_server()
    return list(server.feedback_server.items())
