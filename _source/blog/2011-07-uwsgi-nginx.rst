Запуск django и других python проектов при помощи uwsgi+nginx
#############################################################

:category: Blog
:date: 2011-07-15
:lang: ru
:slug: uwsgi-nginx
:tags: python, uwsgi, nginx, supervisor, django

----

.. contents:: Содержание:

----

.. note:: Редакция от 11/11/2011


.. note:: Статья описывает развертывание python-проектов на linux сервере с использованием
    nginx_, supervisor_, uwsgi_. В интернете уже есть множество материалов на эту тему,
    ниже находится небольшая систематизация моего опыта.

Практически в каждом веб-проекте используется легковесный веб-сервер (**nginx**,
**lighthttpd** и тд), как минимум для генерации статики. При этом довольно часто для
динамической части проекта применяют apache + модули. В один момент мне надоело
ставить nginx и apache одновременно и теперь я использую связку nginx_ + uwsgi_
из-за простоты развертывания, удобства обслуживания и быстродействия.

**UWSGI** — быстрый, легко настраиваемый сервер для WSGI_ приложений, написанный на **C**.

Далее я покажу как настроить и запустить python WSGI_ приложение (в том числе
и с использованием Django_).

.. note:: Сравнение производительности WSGI серверов:
    http://nichol.as/benchmark-of-python-web-servers


Установка зависимостей
======================

Для начала необходимо установить nginx_, uwsgi_. Последние версии nginx_ уже
содержат поддержку WSGI_, поэтому вручную собирать ничего не надо.

.. raw:: html

    <s>Я предпочитаю устанавливать <b>uwsgi</b> с помощью <b>pip</b>.</s>

.. note:: Рассмотрено для debian-based дистрибутивов. Права суперпользователя.

.. code-block:: bash

    # nginx и uwsgi устанавливаем прямо из репозиториев
    # для последних версий uwsgi неоюходимо дополнительно
    # установить пакет: uwsgi-plugin-python
    apt-get install nginx uwsgi uwsgi-plugin-python

Для управления uwsgi_ и множеством других процессов, я использую supervisor_:

.. code-block:: bash

    apt-get install supervisor

.. note:: Если вы получите ошибку **ImportError** поставьте python-модуль
    **elementtree** и повторите установку supervisor_.
    

Конфигурирование и запуск
=========================

.. note:: Файлы с исходным кодом для данной статьи можно найти по адресу:
    https://github.com/klen/klen.github.com/tree/master/_code/uwsgi
    

Предположим у нас есть python-проект расположенный состоящий 
из очень простого WSGI_ приложения (`wsgi.py`):

.. code-block:: python

    def application(environ, start_response):
        status = '200 OK'
        output = 'Pong!'
    
        response_headers = [('Content-type', 'text/plain'),
                            ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]

.. note:: Здесь и далее предполагается, что корневой путь для проекта
    `/home/klen/Projects/klen.github.com/_code/uwsgi`


Создадим конфигурационный файл с настройками uwsgi_ для запуска нашего приложения: `uwsgi.xml`

.. note:: В данном примере рассмотрен XML формат, но можно использовать
    INI или параметры строки запуска


.. code-block:: xml

    <!-- UWSGI XML Configuration File -->
    <uwsgi>

        <!-- Сокет для передачи данных -->
        <socket>/home/klen/Projects/klen.github.com/_code/uwsgi/uwsgi.sock</socket>

        <!-- Путь к виртуальному окружению -->
        <!-- <home>/home/klen/Projects/klen.github.com/_code/uwsgi/.virtualenv</home> -->

        <!-- Нам понадобится включенный python плагин -->
        <plugins>python</plugins>

        <!-- Дополнительный python-путь -->
        <pythonpath>/home/klen/Projects/klen.github.com/_code/uwsgi</pythonpath>

        <!-- Модуль python с определением wsgi приложения -->
        <module>wsgi</module>

        <!-- Количество процессов -->
        <processes>10</processes>

        <!-- Максимальное количество соединений для каждого процесса -->
        <max-requests>5000</max-requests>

        <!-- Максимальный размер запроса -->
        <buffer-size>32768</buffer-size>

        <!-- Убивать каждое соединение требующее больше 30 сек для обработки -->
        <harakiri>30</harakiri>

        <reload-mercy>8</reload-mercy>
        <master />
        <no-orphans />

    </uwsgi>


Создадим конфигурационный файл с настройками для supervisor_: `supervisor.conf`

.. code-block:: ini

    [program:example]
    command=/usr/bin/uwsgi -x /home/klen/Projects/klen.github.com/_code/uwsgi/uwsgi.xml
    user=www-data
    stdout_logfile=/home/klen/Projects/klen.github.com/_code/uwsgi/logs/uwsgi.log
    stderr_logfile=/home/klen/Projects/klen.github.com/_code/uwsgi/logs/uwsgi_err.log
    directory=/home/klen/Projects/klen.github.com/_code/uwsgi
    autostart=true
    autorestart=true
    redirect_stderr=true
    stopsignal=QUIT

.. note::
    Обычно я держу конфигурацию supervisor_ в проекте и создаю
    на нее симлинки в `/etc/supervisor/conf.d`

Настроим **server** в nginx_:

.. code-block:: nginx

    upstream example.proxy {
        ip_hash;
        server unix:///home/klen/Projects/klen.github.com/_code/uwsgi/uwsgi.sock;
    }

    server {

        listen      4444;

        # В продакшен добавьте сюда свой домен
        # server_name example.com;

        access_log  /home/klen/Projects/klen.github.com/_code/uwsgi/logs/nginx_access.log;
        error_log   /home/klen/Projects/klen.github.com/_code/uwsgi/logs/nginx_error.log;

        # Статика у нас будет хранится в папк static в корне проекта
        location ^~ /static/ {
            root /var/www/example;
            expires max;
        }

        location = /favicon.ico {
            rewrite (.*) /static/favicon.ico; 
        }

        location = /robots.txt {
            rewrite (.*) /static/robots.txt; 
        }

        location / {
            uwsgi_pass  example.proxy;
            include     uwsgi_params;
        }
    }


Запуск
======

Создадим ссылку на файлы конфигурации проекта для nginx_ и supervisor_:

.. code-block:: bash

    # создадим папку для логов
    mkdir logs

    # nginx
    ln -s /home/klen/Projects/klen.github.com/_code/uwsgi/nginx.conf /etc/nginx/sites-enabled/uwsgi-example.conf 

    # supervisor
    ln -s /home/klen/Projects/klen.github.com/_code/uwsgi/supervisor.conf /etc/supervisor/conf.d/uwsgi-example.conf

Дадим права на запись всем пользователям:

.. note::
    По хорошему надо просто изменить владельца проекта на www-data.

.. code-block:: bash

    chmod a+w -R /home/klen/Projects/klen.github.com/_code/uwsgi 

Перезапустим nginx_ и supervisor_:

.. code-block:: bash

    /etc/init.d/nginx restart
    /etc/init.d/supervisor stop
    /etc/init.d/supervisor start

Если все прошло успешно, то перейдя по адресу: http://localhost:4444/
вы должны увидеть наше работающее приложение.


Настройка django-проекта
========================

Для Django_ проекта вам необходимо просто изменить `wsgi.py`:

.. code-block:: python

    #!/usr/bin/env python
    import os

    from django.core.handlers.wsgi import WSGIHandler


    os.environ['DJANGO_SETTINGS_MODULE'] = os.environ.get(
        'DJANGO_SETTINGS_MODULE', 'settings')

    application = WSGIHandler()

.. note:: Предпологается, что проект находится в той же директории,
    в противном случае добавьте необходимые пути в sys.path


Управление
==========

.. code-block:: bash

    # Старт проекта
    supervisorctl start example

    # Перезапуск проекта
    supervisorctl restart example

    # Останов проекта
    supervisorctl stop example

    # Статус проекта
    supervisorctl status example

.. note:: Также вы можете использовать параметр uwsgi_ **touch-reload**


Данный способ успешно применяется мной в боевой и девелоперской среде.
Например так работают сайты http://intaxi.ru и http://venturebrothers.ru.


.. _nginx: http://nginx.net/
.. _supervisor: http://supervisord.org/
.. _uwsgi: http://projects.unbit.it/uwsgi/
.. _WSGI: http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
.. _pip: http://pypi.python.org/pypi/pip
.. _Django: http://django-project.com
