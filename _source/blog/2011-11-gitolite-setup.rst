Настройка сервера. Gitolite — хостинг git-репозиториев
######################################################

:category: Blog
:date: 2011-11-18
:lang: ru
:slug: gitolite-setup
:tags: hosting, git, gitolite
:parts: deploy_old

----

.. contents:: Содержание:

----

В `предыдущей <../aws-ru.html>`_ статье я рассказал как создать свой бесплатный
(в течении года) сервер на облаке от `Amazon Web Services <http://aws.amazon.com/>`_.
Пришла пора настроить на нем среду для удобной разработки.

Ниже будет описано создание собственного Git_ репозитория с помощью Gitolite_.

.. note:: Все инструкции в этой статье приводятся для системы
    **Ubuntu Oneiric**, пользователь **ubuntu**.


Начало работы
=============

Первые мои команды на новом сервере:

.. code-block:: bash

    # Обновление системы (да мне нравятся свежие пакеты)
    sudo apt-get update
    sudo apt-get upgrade

    # Утилиты для сборки
    $ sudo apt-get install build-essential
    
    # Конфигурирование локалей
    $ sudo locale-gen ru_RU.UTF-8
    $ sudo locale-gen en_US.UTF-8
    $ sudo dpkg-reconfigure locales



Установка Gitolite_
===================

Git_ распределенная система контроля версий и не нуждается в хостинг-сервере.
Но в таком случае для доступа к репозиторию необходим доступ к файловой системе,
в которой он расположен. В противном случае для синхронизации (команды
разработчиков или кода на сервере) необходим Git_ хостинг с сетевым доступом.

Самые распространенные решения: Gitolite_ и Gitosis_. Я предпочитаю Gitolite_
из-за удобства настройки и установки.

Для начала установим Git_  и Gitolite_ из пакетов:

.. code-block:: bash

    # Установка git и gitolite
    $ sudo apt-get install git gitolite

Теперь нужно создать владельца репозиториев. Обычно используется пользователь
с логином: **git**. Создадим его и выполним под ним настройку Gitolite_:

.. code-block:: bash

    # Создание пользователя git
    $ sudo useradd -m git

    # Копируем свой публичный ssh rsa ключ из домашней директории
    # для настройки управления репозиторием
    $ sudo cp ~/.ssh/id_rsa.pub /home/git/admin.pub

    # Заходим под пользователем git и заканчиваем настройку
    $ sudo su git
    $ cd
    $ gl-setup admin.pub

В этот момент откроется Vim_ с настройками репозитория по-умолчанию. Сохраняя
спокойствие, нажмите `:x` для сохранения и выхода из редактора. Нажмите **Ctrl+D**
для окончания сеанса пользователя **git**. Поздравляю первый этап настройки
закончен, можете закрыть соединение с сервером, дальнейшая настройка будет
произведена на вашей локальной машине.


Управление Gitolite_
====================

Управление Gitolite_ осуществляется с помощью специального репозитория
**gitolite-admin** который уже создан у вас на сервере. Добавление репозиториев
и пользователей, изменения конфигурации производятся через стандартные Git_
операции (commit, push).

Скачаем этот репозиторий на ваш локальный компьютер:

.. note:: Здесь, и далее, я работаю с адресом моей созданной на Amazon VPS:
    `awsdemo.us.to`. Для вас он будет отличаться. Как создать и прикрепить
    свой домен было рассказано в прошлой статье.

.. code-block:: bash

    # -- Ваша локальная машина --
    # git clone git@<your_vps_domain>:gitolite-admin.git
    git clone git@awsdemo.us.to:gitolite-admin.git

Если вы ничего не напутали с ключами и настройками, то **gitolite-admin** будет
скопирован на ваш компьютер.

.. note:: **gitolite-admin** включает в себя две папки. Папка `keys` включает в
    себя файлы с публичными частями rsa ключей пользователей репозитория.
    Папка `conf` содержит файлы конфигурации gitolite.

Посмотрим на файл `conf/gitolite.conf`:

.. code-block:: bash

    repo    gitolite-admin
            RW+     =   admin

    repo    testing
            RW+     =   @all

Он говорит нам о том, что на нашем хостинге доступно два репозитория:
**gitolite-admin** и **testing**, при чем к первому из них доступ на чтение
и запись имеет только пользователь с ключом сохраненным в файле
`keys/admin.pub`, а ко второму все пользователи.

Добавим еще одну запись для нашего будущего Django_-проекта, я назову его `awsdemo`:

.. code-block:: bash

    repo    gitolite-admin
            RW+     =   admin

    repo    testing
            RW+     =   @all

    repo    awsdemo
            RW+     =   admin

Сохраним изменения и отправим их на сервер:

.. code-block:: bash

    $ git commit -am 'Add django repo'
    $ git push origin master

Теперь можно создавать сам проект и привязывать его к удаленному хостингу:

.. code-block:: bash

    # Создание директории для будущего проекта
    $ mkdir -p ~/Projects/awsdemo
    $ cd ~/Projects/awsdemo

    # Создание репозитория
    $ git init

    # Привязываем его к нашему хостингу
    $ git remote add origin git@awsdemo.us.to:awsdemo.git

    # Первый коммит
    $ touch README
    $ git add .
    $ git commit -am "Initial commit"

    # Отправляем изменения на сервер
    $ git push origin master

      Counting objects: 3, done.
      Writing objects: 100% (3/3), 210 bytes, done.
      Total 3 (delta 0), reused 0 (delta 0)
      To git@ec2-174-129-57-41.compute-1.amazonaws.com:django.git
        * [new branch]      master -> master

Все, новый репозиторий создан и доступен для клонирования из Gitolite_

Продолжение: `Настройка сервера. Создаем и разворачиваем django-проект <../deploy-setup-ru.html>`_


.. _Git: http://git-scm.com/
.. _Gitolite: https://github.com/sitaramc/gitolite
.. _Ubuntu: http://ubuntu.com
.. _Gitosis: https://github.com/res0nat0r/gitosis.git
.. _Vim: www.vim.org
.. _Django: www.djangoproject.org
