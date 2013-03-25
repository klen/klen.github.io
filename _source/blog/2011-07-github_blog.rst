Создаем свой персональный сайт на Github.
#########################################

:category: Blog
:date: 2011-07-03
:lang: ru
:slug: github-blog
:tags: python, git, github

----

.. contents:: Содержание:

----

Mало кто знает, что Github_ кроме превосходного хостинга ваших Git_ проектов
может также `хостить <http://pages.github.com/>`_ ваш персональный сайт.
Например на нем расположен этот блог. В своей первой статье я
расскажу как максимально удобно настроить эту функциональность.


Введение
========

Для начала вам нужно быть зарегистрированным пользователем Github_ и уметь
работать с системой контроля версий Git_. Предположим вы готовы.

* Первое, что вам потребуется — это создать на Github_ репозиторий с именем вида: `username.github.com`, где `username` ваш логин на сервисе. Например для этого блога создан репозиторий http://github.com/klen/klen.github.com

* Вторым шагом мы создадим локальный репозиторий и привяжем его к удаленному:

.. note:: В дальнейшем я буду приводить примеры для своего сайта: klen.github.com

.. code-block:: bash

    mkdir ~/Projects/klen.github.com
    cd ~/Projects/klen.github.com
    git init
    echo 'Hello world!' > index.html
    git add .
    git commit -m 'Initial commit'
    git remote add origin git@github.com:klen/klen.github.com.git
    git push -u origin master

Отлично, ваш статический сайт уже готов! В течении 10 минут он появится по адресу:
 `username.github.com`. В дальнейшем он будет обновляться при коммитах в удаленный
 репозиторий.


Использование генераторов статических сайтов
=============================================

Созданный нами сайт не слишком удобен для работы, трудно писать содержание
используя HTML, сложно поддерживать целостность ссылок. Использовать его
например как блог очень затруднительно.

Существует масса проектов генерации статических сайтов и блогов.
При работе с ними фактически вы пишете страницы и статьи в удобном для вас формате,
а затем генератор обновляет структуру сайта. По-умолчанию Github_ уже поддерживает
написанный на ruby генератор Jekyll_. То есть вам необязательно использовать только
HTML синтаксис, из коробки вы можете писать в ваш сайт на Markdown_. Подробнее читайте
в документации `Github Pages`_ и Jekyll_.

Я предпочитаю генерировать страницы локально и проверять результат без выгрузки
содержания на Github_. Мне привычнее работать с Python_ поэтому в качестве генератора
сайта мной используется Pelican_. Ниже я покажу как поставить его и настроить для работы.

Если вы предпочитаете **ruby** дальше можете не читать.


Установка и настройка Pelican
=============================

Предполагается, что вы знакомы с Python_ и VirtualEnv_.

1. Так как мы будем использовать Pelican_ нам необходимо выключить встроенный в Github_ генератор Jekyll_. Это делается добавлением в корень репозитория файла `.nojekyll`.

.. code-block:: bash

    touch .nojekyll
    git add .
    git commit -m 'Disable Jekyll'


2. Теперь создадим и активируем виртуальное окружение для модулей нашего сайта:

.. code-block:: bash

    virtualenv .ve_blog
    source .ve_blog/bin/activate


3. Установим в созданный нами VirtualEnv_ генератор Pelican_ и необходимый для него движок шаблонов Jinja2_:

.. code-block:: bash

    easy_install pelican
    easy_install jinja2


4. Мы будем держать исходники сайта в поддиректории **source**, а созданные статические страницы в корне репозитория, чтобы Github_ их видел.  Создадим файл `source/hello.rst` с нашей первой статьей:

.. code-block:: rst

    Hello world!
    ############

    :slug: hello

    Hello from Pelican!


.. note::
    Я использую синтаксис RST_, но вы можете использовать Markdown_ для своего сайта. Просто сохраняйте файлы с расширением `*.md`
    Pelican_ поддерживает и другие форматы, но надо ставить соответствующие модули.


6. И соберем статику:

.. code-block:: bash

    pelican source -o .

.. note::
    Опция *-o .* заставляет Pelican_ производить сборку статики в корне
    проекта.


    Если все прошло успешно в корне проекта вы увидите несколько **HTML** файлов.
    Откройте `index.html` в браузере и посмотрите на ваш сайт.


7. Теперь наши изменения можно сохранить в Git_ и отправить на Github_.

.. code-block:: bash

    git add .
    git commit -m 'Add virtualenv and setup pelican.'
    git push origin master



Автоматизация
=============

Настроим наш сайт и немного автоматизируем рутинные операции.

1. Создадим файл настроек нашего сайта `source/settings.py`:

.. code-block:: python

    AUTHOR = 'Kirill Klenov'
    SITENAME = 'klen.github.com'
    SITEURL = 'http://klen.github.com'

.. note:: 
    Подробнее про настройки Pelican_, можно прочитать в его документации.


2. Для упрощения сборки создадим sh-файл `.compile`

.. code-block:: bash

    #!/bin/sh

    PRJ_DIR=/home/klen/Projects/klen.github.com

    VE_DIR=$PRJ_DIR/.ve_blog

    # Modify path
    OLD_PATH=$PATH
    PATH="$VE_DIR/bin:$PRJ_DIR:$PATH"
    export PATH

    # Compile static files
    pelican $PRJ_DIR/source -o $PRJ_DIR -s $PRJ_DIR/source/settings.py -v

    # Return PATH
    PATH=$OLD_PATH
    export PATH

И дадим ему права на исполнение:

.. code-block:: bash

    chmod +x .compile

Теперь в директории проекта можно вызывать `./.compile` и собирать статику даже без активации 
виртуального окружения.


3. Следующим шагом создадим Git_ хук для автоматической генерации сайта при коммитах. Создадим и отредактируем файл `.git/hooks/pre-commit`:

.. code-block:: bash

    #!/bin/sh

    PRJ_DIR=/home/klen/Projects/klen.github.com

    $PRJ_DIR/.compile


.. note::
    Не забудьте сделать его исполнемым.
    
При каждом коммите изменений в репозиторий, проект будет пере-собран
автоматически.

На этом нашу предварительную работу по созданию github-сайта можно считать
оконченной. В дальнейшем стоит поподробнее прочитать документацию Pelican_, 
модифицировать стандартную или создать собственную тему оформления и подключить
какой нибудь сервис комментариев.

.. note::

    Как нетрудно догадаться исходники этого блога расположены по адресу: http://github.com/klen/klen.github.com



.. _Github: http://github.com
.. _Git: http://git-scm.com
.. _Github Pages: http://pages.github.com/
.. _Jekyll: http://github.com/mojombo/jekyll/
.. _Pelican: http://docs.notmyidea.org/alexis/pelican/
.. _VirtualEnv: http://pypi.python.org/pypi/virtualenv
.. _Python: http://python.org
.. _Jinja2: http://jinja.pocoo.org/docs/
.. _RST: http://docutils.sourceforge.net/rst.html
.. _Markdown: http://en.wikipedia.org/wiki/Markdown
