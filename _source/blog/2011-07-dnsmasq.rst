Настройка dnsmasq для локальной разработки (linux)
##################################################

:category: Blog
:date: 2011-07-08
:lang: ru
:slug: dnsmasq
:tags: linux, dnsmasq

----

.. contents:: Содержание:

----

В какой-то момент в процессе локальной разработки мне надоело постоянно
редактировать `/etc/hosts` для тестирования очередного развернутого проекта.
Появилось желание настроить "wild local dns" — например чтобы все днс вида
\*.dev.me вели на **localhost**. К сожалению `/etc/hosts` не поддерживает
записи вида \*.bla.bla.bla. Поиск в интернете давал только ссылки на BIND9_,
настраивать который достаточно
`сложно <http://xgu.ru/wiki/%D0%9D%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0_DNS>`_.
Но когда я уже был морально готов воевать с BIND9_, мне на глаза попался более
простой **DNS** сервер — Dnsmasq_. С его использованием задача сильно
упрощается, буквально до нескольких команд.


Установка и использование Dnsmasq
=================================

debian-based (вам понадобятся root права):

.. code-block:: bash

    # Устанавливаем dnsmasq
    apt-get install dnsmasq

    # Редактируем кнфигурацию dnsmasq
    vim /etc/dnsmasq.conf
    #   # Добавляем строку со своим "вируальным доменом для localhost"
    #   address=/dev.me/127.0.0.1

    # Перезапускаем сервис
    /etc/init.d/dnsmasq restart

    # Все, наши локальные поддомены готовы.
    ping dev.me
    ping something.dev.me
    ping another.domain.dev.me

Все работает!


.. _BIND9: http://www.bind9.net/manuals
.. _Dnsmasq: http://en.wikipedia.org/wiki/Dnsmasq
