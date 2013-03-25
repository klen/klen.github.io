from abstract_app.models import Client
from celery.decorators import periodic_task

from .ios import get_feedbacks
from .settings import IOS_CLEAN_INTERVAL


@periodic_task(ignore_result=True, run_every=IOS_CLEAN_INTERVAL)
def parse_async_feedbacks():
    feedbacks = get_feedbacks()
    if feedbacks:
        tokens, _ = zip(*feedbacks)
        Client.objects.filter(token__in=tokens).update(active=False)
    return True
