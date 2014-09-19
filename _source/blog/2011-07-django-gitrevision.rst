Django-gitrevision, автоматическое обновление статики на клиенте
################################################################

:category: Blog
:date: 2011-07-04
:lang: ru
:slug: git-revision
:tags: python, git, django

----

.. contents:: Содержание:

----

В современных веб-проектах, статические файлы (css, js ...) обычно жестко
кешируются с целью экономики трафика и для предупреждения лишней нагрузки на
сервер. В тоже время важно чтобы при обновлении статики, особенно JavaScript
файлов, старые клиенты получили обновленную версию.

В моем проекте используется Git_ и Django_. И вполне логично допустить, что
актуальная версия статики зависит от номера последнего коммита в Git_.

Поэтому когда такая проблема возникла, я взял и написал очень простое
django-приложение для отслеживания текущего Git_ коммита в проекте.

.. note:: На текущий момент данное приложение неактуально тк я сделал http://github.com/klen/dealer
    Последний пакет поддерживает несколько систем контроля версий включая git и mercurial.
    И несколько python веб-фреймворков, а не только Django_.


Установка
=========

Приложение можно установить из PyPi_

.. code-block:: bash

    easy_install django-gitrevision

    # Или с помощью pip

    pip install django-gitrevision


Настройка и использование
=========================

Необходимо добавить `gitrevision` в **INSTALLED_APPS**, settings.py:

.. code-block:: python

    INSTALLED_APPS += 'gitrevision',


Если вы предполагаете использовать `gitrevision` шаблонах (для
обновления статики, этого достаточно) добавьте в settings.py:

.. code-block:: python

    TEMPLATE_CONTEXT_PROCESSORS += 'gitrevision.context_processors.gitrevision',

И используйте переменную `GIT_REVISION` в шаблонах:

.. code-block:: html

    <link href="/test.css?{{ GIT_REVISION }}" rel="stylesheet" type="text/css" media="screen" />
    <script src="/test.js?{{ GIT_REVISION }}"></script>


Если идентификатор коммита нужен во views, хотя мне трудно представить такую
ситуацию, то подключите `gitrevision` в MIDDLEWARE_CLASSES.

.. code-block:: python

        MIDDLEWARE_CLASSES += 'gitrevision.middleware.GitRevision',

Использование в views:

.. code-block:: python

    def superview( request ):
        gitrevision = request.git_revision
        ...

В этом случае нет необходимости подключать CONTEXT_PROCESSOR так как в шаблонах
идентификатор будет доступен через `request.git_revision`.

.. note:: 
    Возможно вам понадобится добавить переменную с путем к вашему
    репозиторию в settings:

    .. code-block:: python

        GIT_PATH = <path_to_your_git_repository>


Заключение
==========

Приложение написано таким образом, что файловые операции происходят единожды
при компиляции проекта. Таким образом нагрузки на сервер не создается.


Теперь в текущих проектах у меня не возникает головной боли по поводу
устаревшей версии статики на клиентах.


.. _Git: http://git-scm.com
.. _Django: http://django-project.com
.. _PyPi: http://pypi.python.org
