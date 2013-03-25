Urbanairship, push-уведомления для мобильных приложений
#######################################################

:category: Blog
:date: 2011-07-16
:lang: ru
:slug: urbanairship
:tags: json, push notification, python, apple, android

----

.. contents:: Содержание:

----

.. note:: Статью про самостоятельную реализацию IOS Push смотрите `здесь <../ios-push-python-ru.html>`_.
   Самостоятельная серверная реализация Android Push рассматривается `тут <../android-push-python-ru.html>`_

Разрабатывая мобильные приложения рано или поздно сталкиваешься с
необходимостью оперативного оповещения клиентов о происходящих на сервере
изменениях. Клиентское приложение иногда связывается с сервером и получает
данные которые его ожидают. Но что делать если приложение не соединено с
сервером или выключено, а оповестить о событиях необходимо?

Для этого практически для всех популярных мобильных платформ (ios, android,
blackberry) компаниями-разработчиками реализована функциональность
Push-уведомлений.

**Push-уведомления** — сообщения которые сервер отправляет
клиенту для информирования его о новых данных. Например это может быть
новое сообщение от знакомого, изменение статуса заказа, появление определенного
товара и так далее.

.. note::
    Для веб-приложений вариант реализации push-уведомлений описывается в статье:
    `Создание сервера оповещений с использованием Tornado и Socket.IO <http://klen.github.com/tornadio_socket-io-ru.html>`_

Практически для каждого типа мобильных устройств данный функционал необходимо
реализовывать отдельно, поэтому для своего последнего проекта я решил
воспользовался специальным сервисом Urbanairship_.

Данный сервис позволяет пользоваться едиными API для отправки уведомлений на
apple, android, blackberry устройства. Позволяет вести статистику и пользоваться
отладочной консолью. Без сложностей переключаться между боевым и разработческим
режимами отправки. И самое главное демократичной ценовой политикой
https://urbanairship.com/pricing/. Бесплатное ограничение в **миллион
уведомлений в месяц** покроет большинство небольших проектов, а если ваше
приложение перерастет этот порог то $0.001 за уведомление (2.8 копейки) при
превышении не должно составить трудностей и это значительно дешевле SMS-сообщений.

В данной статье рассматривается работа c Urbanairship_ на примере iPhone
push-уведомлений.


Регистрация и создание приложения
=================================

1. Регистрируемся на http://urbanairship.com, при регистрации вас попросят
   указать адрес для платежей и действующие данные кредитной карты.

2. Перед созданием приложения на Urbanairship_ нам необходимо получить
   push SSL сертификат. Идем на
   `iOS Provisioning Portal <https://developer.apple.com/ios/manage/overview/index.action>`_
   и получаем **Development** и **Production Push SSL Certificate** в формате
   `*.cer`. Получив их на любое Apple Mac устройство конвертируйте в
   Personal Information Exchange (.p12) формат.

3. Теперь мы готовы зарегистрировать наше приложение на Urbanairship_. Идем по
   адресу https://go.urbanairship.com/apps/ и создаем два новых приложения 
   ( example-production, example-development ) выбирая соответственно Production
   или Development режимы и загружая соответствующие сертификаты.
   Для каждого из режимов записываем `Application Key` и
   `Application Master Secret` они нам понадобятся для работы с API.

.. note::
    Рекомендуется создавать по отдельному приложению для production и
    development режимов.


Отправка push-уведомлений
=========================

Реализуем с помощью python механизм push-уведомлений для нашего приложения.
Прежде всего рассмотрим каким образом это все реализовано на примере IOS
устройств.

Для работы службы уведомлений требуется IOS 3.0 или выше, подключение к
Интернету и поддержка в вашей мобильной программе. Чтобы получать уведомления
от программы, ее необходимо открыть как минимум один раз. Когда IOS устройство
находится в активном режиме (экран включен) прием уведомлений осуществляется в
любое время, в противном случае через каждые 15 минут.

Для отправки уведомления на устройство сервер должен знать **Device token**
который приложение получает при регистрации в **Apple Push Notification
Service**. В уведомлениях можно использовать звуки, значки, текстовые сообщения.

.. note::
    `Urbanairship push documentation <http://urbanairship.com/docs/index.html>`_

Резюмируя:

    - Приложение должно зарегистрироваться в Apple и получить **Device Token**;

    - Приложение должно сообщить **Device Token** серверу (например
       http-заголовком);

    - Для отправки уведомления сервер делает http запрос к API Urbanairship_,
      с JSON данными.

Реализация на python (django) может выглядеть следующим образом:

.. code-block:: python

    from urllib import urlencode
    from urllib2 import urlopen, Request, URLError

    from django.utils import simplejson
    from django.conf import settings
    from celery.decorators import task

    @task(ignore_result=True, max_retries=3, default_retry_delay=10)
    def send_ios(message, sound=None, device_token=None):
        """ Send IOS push notification
            with urbanairship service.
            Celery async task.
        """
        if isinstance(message, basestring):
            message = dict(alert = message)

        if device_token:
            try:
                return urlopen(Request(
                    settings.URBANSHIP_PUSH_URL,
                    simplejson.dumps(dict(
                        device_tokens = [ device_token ],
                        aps = dict(sound=sound, alert=message.get('alert'),
                                    data=message.get('data'))
                    )),
                    headers = {
                        'Authorization': 'Basic %s' % base64.b64encode(
                            "%s:%s" % (settings.URBANSHIP_APP_KEY,
                                        settings.URBANSHIP_MASTER_SECRET)),
                        'Content-type': 'application/json',
                    },
                ), timeout=10)

            except URLError, e:
                _send_ios.get_logger().error("urbanairship server is unresponsible, cannot send ios notification")
                _send_ios.retry(exc=e)

.. note::
    В данном примере я использовал Celery_ для выполнения асинхронного оповещения.
    Если на вашем проекте очереди задач не используются уберите декоратор `task` и
    обвязку кода отправки в `try ... except`.

В настройках проекта мы должны указать ключи: **'URBANSHIP_PUSH_URL,
URBANSHIP_APP_KEY, URBANSHIP_MASTER_SECRET'** полученные нами ранее. В своей
разработке я стартую продакшен и дев сервера с разными настройками,
соответственно с разными ключами для Urbanairship_.

Обратите внимание, что для использования этой функции нам необходимо знать
**device_token**, который нам должно сообщить приложение.

Использование:

.. code-block:: python

    # simple message
    send_ios('Hello', device_token='FAKEDEVICETOKEN')

    # message with sound
    send_ios('Beep', sound='default', device_token='FAKEDEVICETOKEN')

    # message with data
    send_ios({
        alert = 'Some data',
        data = {
            order: 999,
            status: 'updated',
        }
    }, sound='default', device_token='FAKEDEVICETOKEN')

Если отправка не происходит откройте приложение в Urbanairship_ в режиме
просмотра и посмотрите сообщения в консоли (для отладки должен быть
активирован чекбокс debug в настройках (production, development) приложения).


Заключение
==========

Мы рассмотрели push-уведомления для IOS устройств, но фактически уже имеем
поддержку android или blackberry. Необходимо только изменять JSON данные в
запросе к API Urbanairship_.

Мой опыт взаимодействия с Urbanairship_ на протяжении последних трех месяцев
исключительно позитивный.


    * `Urbanairship push documentation <http://urbanairship.com/docs/index.html>`_

    * `Apple Push Notification Service Programming Guide <http://developer.apple.com/library/ios/#documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/Introduction/Introduction.html>`_

    * `Android Cloud to Device Messaging Framework <http://code.google.com/android/c2dm/>`_




.. _Urbanairship: http://urbanairship.com/
.. _Celery: http://celeryproject.org/
