import os.path as op

from apns import APNs, Payload


KEYS_FILE = op.abspath(op.join(op.dirname(__file__), 'fakekey.pem'))

assert op.exists(KEYS_FILE)


def get_server(use_sandbox=False, keys_file=KEYS_FILE):
    " Create and return production or develop server. "
    return APNs(use_sandbox=use_sandbox, cert_file=keys_file, key_file=keys_file)


def send_notify(token, server=None, **payloads):
    " Send simple device notify. "
    server = server or get_server()
    return server.gateway_server.send_notification(token, Payload(**payloads))


def get_feedbacks(server):
    " Get inactive tokens. "
    return list(server.feedback_server.items())
