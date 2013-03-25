Настройка сервера. Создаем и разворачиваем django-проект
########################################################

:category: Blog
:date: 2011-11-26
:lang: ru
:slug: deploy-setup
:tags: hosting, deploy, makesite, django, uwsgi, nginx

----

.. contents:: Содержание:

----

**Создание и настройка полноценного сервера разработки:**

1. `Год облачного хостинга от Amazon — бесплатно <../aws-ru.html>`_
2. `Настройка сервера. Gitolite — хостинг git-репозиториев <../gitolite-setup-ru.html>`_
3. **Настройка сервера. Создаем и разворачиваем django-проект**

----

В `предыдущей <../gitolite-setup-ru.html>`_ статье показывалось как поднять и настроить
хостинг Git_ репозиториев на своем сервере. Ниже будет описано создание Django_ проекта,
развертывание его на сервере и настройка авто-обновления кода.

.. note:: Все инструкции в этой статье приводятся для системы
    **Ubuntu Oneiric**, пользователь **ubuntu**.


Makesite
========

Настройка, развертывание и обновление сайтов — операции, требующие автоматизации. Есть множество
утилит для этого, например Capistrano_ (ruby) или Fabric_ (python). В свое время эта
задача встала и передо мной.
Были определены следующие требования:

- В основе системы должны находится **shell** скрипты;
- Развертывание проекта должно производится одной командой;
- Элементарное обновление или удаление проектов;
- Каждый экземпляр проекта привязан к ветке репозитория;
- Настройки всех проектов могут быть заданы как глобально, так и в момент развертывания;
- Легкость настройки и создания шаблонов;
- Автономность уже развернутого проекта;

Беглый осмотр существующих решений привел к необходимости в очередной раз писать свой велосипед.
В итоге на свет появился Makesite_. Описание всех принципов его работы выходит за рамки данной статьи.

Основное его предназначение — автоматическое создание будущей структуры сайта. Файлов
конфигурации сервера и скриптов обновления и перезапуска. Вы можете изменять и редактировать
параметры этих файлов после развертывания.


Установка и настройка Makesite
==============================

.. note:: Данные действия выполняются на сервере

Для начала работы на нашем сервере потребуется установить и настроить Makesite_.
Рекомендуется проводить установку при помощи **setuptools**:

.. code-block:: bash

    # Устанавливаем setup-tools
    sudo apt-get install python-setuptools python-pip

    # Устанавливаем makesite
    sudo easy_install makesite

    # Или при помощи Pip
    sudo pip install makesite


Теперь нам необходимо решить в какой директории будут развернуты наши проекты и указать ее для Makesite_.
Обычно я использую `/var/www`. Чтобы не вводить этот путь при каждой операции, определим системную переменную `$MAKESITE_HOME`. Удобно сразу это сделать при помощи следующей команды:

.. code-block:: bash

    # Создаем директорию для хранения наших будущих сайтов
    $ sudo mkdir /var/www

    # Выводим и проверяем настройки bash
    $ makesite shell -p /var/www

    # Записываем их в ваш ~/.bashrc
    $ makesite shell -p /var/www >> ~/.bashrc

    # Загружаем настройки для текущего сеанса
    $ source ~/.bashrc


Создаем корневой файл конфигурации в указанной нами директории `/var/www/makesite.ini`.

.. note:: В примерах используется адрес созданного в предыдущих статьях AWS_ сервера: **awsdemo.us.to**.

.. code-block:: ini

    [Main]

    # Указываем источник получения кода проектов по умолчанию
    # В данном случае будет использоваться созданный нами репозиторий
    # Префикс 'git+' указывает Makesite на способ получения
    # В настройках можно применять переменные, в данном случае будет
    # производиться поиск репозитория по имени разворачиваемого проекта
    src = git+git@awsdemo.us.to:%(project)s.git

    # Доменное имя для создаваемых конфигураций сайтов
    # Можно было сделать например так:
    # domain = %(branch)s.%(project)s.us.to
    # Но так как полученный нами бесплатный DNS не поддерживает Wildcard записи,
    # поступим проще:
    domain = %(project)s.us.to

    # Режим деплоя (это всего лишь переменная которую можно использовать в шаблонах)
    mode = dev

Создание этого файла необязательно, но он здорово упрощает развертывание. В любом случае
у вас всегда есть возможность изменять конфигурации после развертывания.


Создание проекта
================

.. note:: Данные действия выполняются локально

Перейдем к репозиторию `awsdemo` на нашей локальной машине, который мы создали в 
прошлой статье и превратим его в Django-проект.

.. code-block:: bash

    # Переходим в директорию нашего проекта
    $ cd ~/Projects/awsdemo

    # Создаем новый django-проект
    $ django-admin.py startproject aws

    # Переносим файлы из созданного проекта в наш репозиторий
    $ mv aws/* . && rm -r aws

    # Сохраняем изменения в git
    $ git add .
    $ git commit -m 'Start new django-project'

Теперь его надо подготовить к деплою.

.. note:: Файлы с исходным кодом Django-проекта можно найти по адресу:
    https://github.com/klen/klen.github.com/tree/master/_code/awsdemo


Подготовка Django-проекта к деплою
==================================

.. note:: Данные действия выполняются локально

Рекомендуется, но совсем необязательно, создавать в корневой
директории проекта файл конфигурации Makesite_ с основными параметрами деплоя.

Создадим файл `makesite.ini`:

.. code-block:: ini

    [Main]
    # Шаблоны Makesite которые будут применятся для нашего сайта
    # всегда есть возможность создать собственные шаблоны
    # в том числе и в хранимые с исходниками проекта
    template=virtualenv,django,uwsgi

Для шаблона `virtualenv` (он создает и обновляет при необходимости
виртуальное окружение проекта) необходимо создать файл с зависимостями.

`requirements.txt`:

.. code-block:: python

    # Django
    Django==1.3

Для шаблона `uwsgi` (он запускает наш проект с помощью uwsgi и nginx)
необходимо создать файл определяющий наше wsgi-приложение.

`wsgi.py`:

.. code-block:: python

    #!/usr/bin/env python
    from os import environ
    from django.core.handlers.wsgi import WSGIHandler

    environ['DJANGO_SETTINGS_MODULE'] = environ.get(
        'DJANGO_SETTINGS_MODULE', 'settings')

    application = WSGIHandler()

Следующее, что необходимо сделать это поправить `settings.py`
изменив его следующим образом (включаем базу данных, интерфейс администрирования,
определяем путь к STATIC_ROOT и правим urlconf):

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'aws.db',
    ...

    from os import path as op
    DEPLOY_DIR = op.dirname(op.dirname(__file__))
    STATIC_ROOT = op.join(DEPLOY_DIR, 'static')

    ...

    ROOT_URLCONF = 'urls'

    ...

    # Uncomment the next line to enable the admin:
    'django.contrib.admin',

    ...

И последнее создадим фикстуру для создания первого пользователя `initial_data.json`
(login: admin, pasword: admin):

.. code-block:: javascript

    [{
            "model": "auth.user",
            "pk": 1,
            "fields": {
                "username": "admin", 
                "first_name": "Darth", 
                "last_name": "Vader", 
                "is_active": true, 
                "is_superuser": true, 
                "is_staff": true, 
                "last_login": "2000-01-01 00:00:00", 
                "groups": [], 
                "user_permissions": [], 
                "password": "sha1$bb19a$51b2bac8dd83c30e6cf6694bf3049241a14124ea", 
                "email": "admin@admin.admin", 
                "date_joined": "2000-01-01 00:00:00"
            }}]

Наш проект готов к деплою.


Создание ключей для клонирования репозитория
============================================

.. note:: Данные действия выполняются на сервере

Деплоить будем из нашего репозитория. Чтобы это возможность появилась,
надо или перенести свой приватный ключ на сервер или создать новый и дать
на него доступ в **gitolite-admin**.

Я предпочитаю второй вариант:

.. code-block:: bash

    # Переходим в нашу домашнюю .ssh директорию
    $ cd ~/.ssh

    # Создаем отдельный ключ для makesite (укажите makesite в имени файла)
    # без паролей
    $ ssh-keygen
      Generating public/private rsa key pair.
      Enter file in which to save the key (/home/ubuntu/.ssh/id_rsa): makesite
      Enter passphrase (empty for no passphrase): 
      Enter same passphrase again: 
      Your identification has been saved in makesite.
      Your public key has been saved in makesite.pub.

    # Копируем ключ в id_rsa
    $ cp makesite id_rsa
    $ cp makesite.pub id_rsa.pub

Полученный ключ надо подключить к нашему репозиторию, путем редактирования `gitolite_admin` (подробности в предыдущей статье). Вкратце ваш порядок действий:

1. Скопировать ключ `~/.ssh/makesite.pub` в `gitolite-admin/keydir/makesite.pub` (например при помощи **scp**)
2. Обновить параметры доступа к `awsdemo` в файле `gitolite-admin/conf/gitolite.conf` (добавить строчку `RW+  makesite`)
3. Сделать коммит с изменениями и пуш на сервер.

Теперь можно проверить работу с репозиторием на стороне сервера:

.. code-block:: bash

    git clone git@awsdemo.us.to:awsdemo.git /tmp/aws

В случае успеха репозиторий должен быть скопирован с удаленного сервера иначе вы, что-то неправильно сделали
с ключами.


Установка зависимостей
======================

.. note:: Данные действия выполняются на сервере

Дадим команду Makesite_ на деплой нашего проекта:

.. code-block:: bash

    makesite install awsdemo

Помните мы указали строку "src = git+git@awsdemo.us.to:%(project)s.git" в `/var/www/makesite.ini`, она говорит Makesite_ где получать исходники проекта. То есть вышеприведенная команда по факту транслируется следующим образом: ::

    makesite install awsdemo --src git+git@awsdemo.us.to:awsdemo.git

.. note:: Makesite_ поддерживает установку из пути файловой системы,
    или git, mercurial (hg+), subversion (svn+) систем контроля версий

Вывод команды будет приблизительно таким: ::

    Clone src: git+git@awsdemo.us.to:awsdemo.git
    --------------------------------------------
    Cmd: /usr/bin/git clone git@awsdemo.us.to:awsdemo.git /tmp/tmpkWznFx/source
    remote: Counting objects: 12, done.
    remote: Compressing objects: 100% (9/9), done.
    remote: Total 12 (delta 1), reused 0 (delta 0)
    Receiving objects: 100% (12/12), done.
    Resolving deltas: 100% (1/1), done.

    Deploy templates: base,src-git,virtualenv,supervisor,nginx,uwsgi
    ----------------------------------------------------------------
    Prepare template: base
    Prepare template: src-git
    Prepare template: virtualenv
    Prepare template: supervisor
    Prepare template: nginx
    Prepare template: uwsgi

    Check requirements
    ------------------
    Cmd: sudo chmod +x /tmp/tmpkWznFx/service/*.sh
    Cmd: /bin/bash /tmp/tmpkWznFx/service/base_check.sh
    Cmd: /bin/bash /tmp/tmpkWznFx/service/virtualenv_check.sh
    Error: Command 'virtualenv' not found!
    Install python-virtualenv package

    Command '/bin/bash /tmp/tmpkWznFx/service/virtualenv_check.sh' returned non-zero exit status 127
    See log: /tmp/tmp8IAJYB


Он говорит нам о том, что на стадии проверки зависимостей Makesite_ прервал установку.
Команда `virtualenv` не была найдена в системе.

Мы можем поставить `python-virtualenv` и повторить попытку, но споткнемся на `nginx`, `uwsgi` или других зависимостях. Поэтому поставим все сразу одной командой.

.. code-block:: bash

    sudo apt-get install python-virtualenv nginx uwsgi uwsgi-plugin-python nginx supervisor
    sudo /etc/init.d/nginx start


Установка и удаление проекта
============================

.. note:: Данные действия выполняются на сервере

Теперь повторим деплой нашего проекта:

.. code-block:: bash

    $ makesite install awsdemo

Эта команда создаст следующую структуру директорий: ::

    /var/www/master/
                awsdemo/
                    |
                    |-deploy/      # Файлы конфигурации
                    |-logs/        # Логи nginx, supervisor, uwsgi
                    |-media/       # Папка для загружаемых файлов
                    |-service/     # Скрипты для обслуживания проекта
                    |-source/      # Исходный код проекта
                    |-static/      # Статика проекта
                    |-.virtualenv/ # Виртуальное окружение проекта
                    |-makesite.ini # Параметры проекта
                    |-.makesite    # Список шаблонов проекта

Сайт уже запущен и работает. Makesite_ скачал исходники, развернул виртуальное окружение,
создал файлы конфигурации nginx, supervisor, uwsgi и подключил их, выполнил синхронизацию
базы данных, скопировал файлы статики, а также создал shell скрипты для обновления,
удаления и перезапуска проекта.

.. image:: sources/awsdemo2.png

Для пробы удалим развернутый проект: 

.. note:: В bash, для большинства команд Makesite_, работает автодополнение.

.. code-block:: bash

    # Указываем короткое имя проекта (ветка.проект)
    $ makesite uninstall master.awsdemo

    # Или можно указать полный путь
    $ makesite uninstall /var/www/awsdemo/master

Проект удален из системы, nginx и supervisor перезагружены. Теперь можно развернуть его
снова вышеприведенной командой.


Обновление проекта
==================

.. note:: Данные действия выполняются локально

Изменим что-нибудь в нашем проекте, например добавим `views.py`: 

.. code-block:: python

    from django.http import HttpResponse


    def home(request):
        return HttpResponse("Hello from makesite!")

Подключим его в `urls.py`:

.. code-block:: python

    ...

    # Examples:
    url(r'^$', 'views.home', name='home'),

    ...

Сохраним и отправим изменения на сервер. Теперь на сервере достаточно ввести
команду `makesite update master.awsdemo`, чтобы наш сайт обновился. При этом новые
зависимости, миграции, статические файлы Makesite_ обработает самостоятельно.

В рамках данной статьи я планировал показать как создать свой хук на обновление репозитория
в gitolite, чтобы git push в удаленный репозиторий вызывал автоматическое обновление
соответствующих сайтов (по факту makesite update), но статья и так получилась достаточно длинной,
поэтому эта задача предлагается к выполнению в качестве домашнего задания.

.. note:: Подробная статья про работу с Makesite_ находится в моих ближайших планах


.. _Makesite: https://github.com/klen/makesite
.. _Django: http://djangoproject.org
.. _uwsgi: http://projects.unbit.it/uwsgi/
.. _nginx: http://nginx.net/
.. _Git: http://git-scm.com/
.. _Capistrano: https://github.com/capistrano/capistrano
.. _Fabric: http://docs.fabfile.org/en/1.3.3/index.html
.. _AWS: http://aws.amazon.com/
