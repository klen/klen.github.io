Серверная реализация Android C2DM Push уведомлений (python)
###########################################################

:category: Blog
:date: 2012-04-03
:lang: ru
:slug: android-push-python
:tags: android, push, c2dm, python, django

----

.. contents:: Содержание:

----

**Статьи по теме**

1. `Urbanairship, push-уведомления для мобильных приложений <../urbanairship-ru.html>`_
2. `IOS Push Уведомления <../ru-ios-push-python.html>`_

----

Настало время рассказать, как реализовать серверную поддержку Push_ уведомлений для Android_. Эта возможность появилась
в мобильной системе начиная с версии **2.2** (API8). Ниже я рассмотрю реализацию на Python_, но для программиста владеющего
другими языками, не должно составить труда справиться самостоятельно.

.. note:: Исходные коды для данной статьи можно увидеть по адресу: https://github.com/klen/klen.github.com/tree/master/_code/android-push

Введение
========

.. image:: /static/img/android-push1.png

Эта простая схема описывает работу с C2DM_ сервисом. Ваше Android_ приложение (**APP**) регистрируется в C2DM_ сервисе
(например при запуске) и отправляет полученный регистрационный код серверу (**APP SERVER**).

Теперь сервер (**APP SERVER**) используя полученный регистрационный код и специальный токен может сформировать специальный
HTTP-запрос сервису C2DM_, который в свою очередь отправит Push_ сообщение устройству на котором запущена ваша программа.

.. note:: По-умолчанию в C2DM_ установлена квота на отсылку не более 200000 уведомлений в день.
            http://code.google.com/android/c2dm/quotas.html


Подготовка к работе
===================

Для начала необходимо зарегистрировать ваше приложение в C2DM_ по адресу: http://code.google.com/android/c2dm/signup.html

.. image:: /static/img/android-push2.png

Вам потребуется указать ваш действующий Google-аккаунт и доменное имя вашего приложения. Вы должны получить на почту письмо
с подтверждением. После регистрации вашему приложению будет добавлена возможность получать Push-уведомления с
учетом действующих в C2DM_ квот.

.. note:: Настройка поддержки Push_ уведомлений на стороне приложения в данной статье не рассматривается.
            Вы можете изучить например эту статью: `C2DM Написание Android клиента <http://prodroid.com.ua/?p=66>`_


Получение токена для сервера
============================

Получение авторизационного токена для сервера подробно рассматривается в документации: `ClientLogin for Installed Applications <https://developers.google.com/accounts/docs/AuthForInstalledApps>`_. Резюмируя данный документ: для получения токена, нам надо сформировать **POST** запрос со следующими параметрами:

=============== =============================================================
**accountType**	HOSTED_OR_GOOGLE
**Email**	our@email.here (email аккаунта регистрировавшего C2DM)
**Passwd**	our_password_here (пароль)
**service**	ac2dm
**source**	our.app идентификатор для логирования (например доменное имя)
=============== =============================================================

Пример запроса: ::

    POST /accounts/ClientLogin HTTP/1.0
    Content-type: application/x-www-form-urlencoded

    accountType=HOSTED_OR_GOOGLE&Email;=jondoe@gmail.com&Passwd;=north23AZ&service;=cl&source=Gulp-CalGulp-1.05

Сделать это можно например используя Curl_ (Замените *ACCOUNT*, *PASSWORD*, *SOURCE* на ваши реквизиты): ::

    curl -X POST https://www.google.com/accounts/ClientLogin -d Email=ACCOUNT -d Passwd=PASSWORD -d source=SOURCE -d accountType=HOSTED_OR_GOOGLE -d service=ac2dm

В третьей строке *Auth=...* и будет ваш искомый токен. Сохраните его в надежном месте.


Отправка Push уведомлений
=========================

Отправка уведомлений описана в разделе: `How the Application Server Sends Messages <http://code.google.com/android/c2dm/index.html#push>`_.
Поддерживаются следующие параметры:

==================================== ================================================================================
**registration_id**                  Ключ регистрации, полученный приложением от C2DM_ и переданный серверу приложений
**collapse_key**                     Название группы сообщений.
**Authorization: GoogleLogin auth=** Токен авторизации (передается в заголовке)
data.<key>                           Набор дополнительных данных в формате key-value
delay_while_idle                     Флаг отложенной доставки. Сообщение может быть доставлено позже.
==================================== ================================================================================

Этих данных достаточно, чтобы написать простой код (для работы с HTTP я использую замечательную библиотеку Requests_):

.. code-block:: python

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

        return response  #**


Теперь отправлять нотификации можно так: 

.. code-block:: python

    send_notify('device-registration-id-here', message='test', sound='test')


Интеграция с Django
===================

При интеграции с Django_ проектом стоит подумать об асинхронности запросов в C2DM_.

Асинхронность достигается использованием Celery_.

.. code-block:: python

    from celery.decorators import task
    from android import send_notify

    @task(ignore_result=True, max_retries=2, default_retry_delay=10, priority=1)
    def _async_android_push(token, payloads, **kwargs):
        return send_notify(token, **payloads)


    def send_async_android_notify(token, **payloads):
        return _async_android_push.apply_async(args=(token, payloads))  # Fix rst**


Мысли на будущее: отключение недействительных устройств, массовые рассылки и проверка доставки.


.. _Push: http://ru.wikipedia.org/wiki/%D0%A2%D0%B5%D1%85%D0%BD%D0%BE%D0%BB%D0%BE%D0%B3%D0%B8%D1%8F_Push
.. _Urbanairship: http://urbanairship.com/
.. _Celery: http://celeryproject.org/
.. _C2DM: http://code.google.com/android/c2dm/
.. _Python: http://python.org
.. _Django: http://django-project.com
.. _Android: http://ru.wikipedia.org/wiki/Android
.. _Requests: http://docs.python-requests.org/en/latest/index.html
.. _Curl: http://ru.wikipedia.org/wiki/CURL
