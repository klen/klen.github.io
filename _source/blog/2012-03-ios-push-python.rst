Серверная реализация IOS Push уведомлений (python)
##################################################

:category: Blog
:date: 2012-03-20
:lang: ru
:slug: ios-push-python
:tags: ios, push, iphone, ipad, python, apns, django

----

.. contents:: Содержание:

----

.. image:: /static/img/push.jpg

Я уже писал `статью <../urbanairship-ru.html>`_ про реализацию Push_ уведомлений с использованием сервиса Urbanairship_.
У этого способа есть ряд преимуществ и недостатков. Преимущества я описал в вышеприведенной статье, недостаки сервиса в
его лимитах на количество бесплатных сообщений и периодических отключениях на техническое обслуживание.

Сегодня мы рассмотрим реализацию IOS_ Push_ уведомлений своими руками для Python_ программ.

.. note:: Исходные коды для данной статьи можно увидеть по адресу: https://github.com/klen/klen.github.com/tree/master/_code/ios-push


Введение
========

IOS_ Push_ уведомления бывают двух видов: локальные и удаленные. Локальные инициируются приложением на стороне
клиента и в данной статье не рассматриваются. Удаленные уведомления отсылаются со стороны сервера на клиентское приложение
при помощи службы APNS_ (Apple Push Notification Service). Процесс выглядит следующим образом:

.. image:: /static/img/apns-scheme.jpg

1. Приложение регистрируется в APNS_ и получает Device Token;
2. Приложение сообщает Device Token нашему серверу;
3. Теперь сервер может установить SSL_ соединение с APNS_ и отправить Push_ уведомление;


Получение и конвертация сертификата
===================================

Push_ сертификаты для приложений можно получить на `iOS Provisioning Portal <https://developer.apple.com/ios/manage/overview/index.action>`_.

.. image:: /static/img/ios-push.png

Выберите свое приложение и зайдите в раздел настроек: ``Configure``.

.. image:: /static/img/ios-push2.png

Скачайте production и development сертификаты (``*.cer``). Возможно вам потребуется предварительно включить
Push_ нотификации для своего приложения и создать их.

.. image:: /static/img/ios-push3.png

Дальнейшие действия лучше провести на компьютере с OSX. Импортируйте полученные сертификаты и экспортируйте их в формате **p12**.
Вероятно вам потребуется ключ разработчика с которым были созданы CSR запросы.

.. image:: /static/img/ios-push4.png

Полученный файл в формате **p12** необходимо переконвертировать в pem. Для этой задачи я написал простенький shell скрипт.

https://github.com/klen/klen.github.com/blob/master/_code/ios-push/convert12.sh

Сконвертируем с его помощью полученный от Apple Dev сертификат в нужный нам формат:

.. code-block:: bash

    # Получим и подготовим скрипт конвертации
    wget https://raw.github.com/klen/klen.github.com/master/_code/ios-push/convert12.sh && chmod +x convert12.sh

    # Сконвертируем полученные от Apple сертификаты
    ./convert12 convert pushprod.p12
    ./convert12 convert pushdev.p12

В процессе у вас будет запрошен пароль на сертификаты, если они создавались без пароля, просто нажмите `Enter`.
Результатом этой операции будут ``pem`` файлы с теми же названиями.

Этим же скриптом их можно протестировать, что в дальнейшем избавит от множества проблем при отладке:

.. code-block:: bash

    # В результате должно быть установлено соединение с Apple
    ./convert12 test pushprod.pem prod
    ./convert12 test pushdev.pem dev

Если соединение сразу сбрасывается или выводятся SSL ошибки, вы что-то сделали неправильно.


Реализация IOS Push в python-приложениях
========================================

В своих проектах я использую PyAPNs_ библиотеку. Простой файл обвязка вокруг нее реализует все основные задачи:
`push.py <https://github.com/klen/klen.github.com/blob/master/_code/ios-push/push.py>`_

.. code-block:: python

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
        return list(server.feedback_server.items())  # Fix rst**


Пример использования:

.. code-block:: python

    from push import send_notify, get_server

    token_hex = 'b5bb9d8014a0f9b1d61e21e796d78dccdf1352f23cd32812f4850b87'
    result = send_notify(token_hex, alert="Hello world!", sound="default")

Вполне возможно, что токен от приложения будет приходить к вам в формате Base64_, тогда перед сохранением
необходимо проделать следующие преобразования.

.. code-block:: python

    import binascii
    from base64 import urlsafe_b64decode

    def fix_token(token):
        token = token.strip()
        token = token.encode('utf-8') if isinstance(token, unicode) else token
        token = urlsafe_b64decode(token + '=' * (4 - len(token) % 4))
        token = binascii.hexlify(token)


Интеграция с Django
===================

При интеграции с Django_ проектом необходимо подумать о переключении между **developer** и **production**
и об асинхронности запросов в APNS_.

Асинхронность достигается использованием Celery_.

.. code-block:: python

    from celery.decorators import task
    from ios import send_notify

    @task(ignore_result=True, max_retries=2, default_retry_delay=10, priority=1)
    def _async_ios_push(token, payloads, **kwargs):
        return send_notify(token, **payloads)


    def send_async_ios_notify(message, token=None):
        " Send IOS push notification. "
        if not token:
            return False

        if isinstance(message, basestring):
            message = dict(alert=message)

        data = dict(item for item in message.iteritems() if not item[0] in ['alert', 'sound'])

        return _async_ios_push.apply_async(args=(token, dict(
            sound=message.get('sound', 'default'),
            alert=message.get('alert'),
            custom=dict(data=data),
        )))  # Fix rst**


Стоит подумать и об отключении неактивных устройств: ``tasks.py``:

.. code-block:: python

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
        return True  # Fix rst*

Полностью пример модуля для Django_ вы можете увидеть по ссылке: https://github.com/klen/klen.github.com/tree/master/_code/ios-push/django/push


Написать функцию для асинхронной **broadcast** рассылки сообщений множеству клиентов, предлагается для самостоятельного
написания в качестве домашнего задания.


.. _Push: http://ru.wikipedia.org/wiki/%D0%A2%D0%B5%D1%85%D0%BD%D0%BE%D0%BB%D0%BE%D0%B3%D0%B8%D1%8F_Push
.. _Urbanairship: http://urbanairship.com/
.. _Celery: http://celeryproject.org/
.. _IOS: http://ru.wikipedia.org/wiki/Apple_iOS
.. _APNS: http://en.wikipedia.org/wiki/Apple_Push_Notification_Service
.. _Python: http://python.org
.. _PyAPNs: https://github.com/simonwhitaker/PyAPNs
.. _Base64: http://ru.wikipedia.org/wiki/Base64
.. _Django: http://django-project.com
.. _SSL: http://ru.wikipedia.org/wiki/SSL
