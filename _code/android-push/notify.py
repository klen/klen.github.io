import requests

from .settings import C2DM_URL, C2DM_TOKEN


class AndroidNotifyError(Exception):
    pass


def send_notify(registration_id, collapse_key="default", delay_while_idle=True, **payloads):
    headers = dict(Authorization='GoogleLogin auth=%s' % C2DM_TOKEN)
    data = {'registration_id': registration_id,
            'collapse_key': collapse_key,
            'delay_while_idle': True}

    for(k, v) in payloads.iteritems():
        data["data.%s" % k] = v

    response = requests.post(C2DM_URL, headers=headers, data=data, verify=False)

    if response.ok and 'Error' in response.content:
        _, error_type = response.content.split('=', 1)
        raise AndroidNotifyError(error_type)

    elif response.status_code == 401:
        raise AndroidNotifyError('ClientLogin invalid.')

    elif response.status_code == 503:
        raise AndroidNotifyError('Service temporarily unavailable.')

    return response
