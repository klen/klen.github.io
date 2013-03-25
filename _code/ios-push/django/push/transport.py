from celery.decorators import task

from .ios import send_notify


@task(ignore_result=True, max_retries=2, default_retry_delay=10, priority=1)
def _async_ios_push(token, payloads, **kwargs):
    return send_notify(token, **payloads)


def send_async_ios_notify(message, device_token=None):
    """ Send IOS push notification
        with urbanairship service.
    """
    if not device_token:
        return False

    if isinstance(message, basestring):
        message = dict(alert=message)

    data = dict(item for item in message.iteritems() if not item[0] in ['alert', 'sound'])

    return _async_ios_push.apply_async(args=(device_token, dict(
        sound=message.get('sound', 'default'),
        alert=message.get('alert'),
        custom=dict(data=data),
    )))
