Создание python-пакетов (aka setup scripts)
###########################################

:category: Blog
:date: 2012-06-13
:lang: ru
:slug: create-python-packages
:tags: python, setuptools, distutils, distribute

----

.. contents:: Содержание:

----

Одна из действительно полезных вещей в python — это система скриптов установки. Любой, серьезно
увлекающийся python-программированием разработчик рано или поздно сталкивается с ней.
Но из-за гибкости инструментария скриптов установки, их документация весьма раздута.
На текущий момент имеется набор утилит (setuptools_, distutils_, distribute_) выполняющих
одинаковые задачи.

.. image:: sources/state_of_packaging.jpg

В данной статье я на конкретных примерах покажу как создать и настроить простой python-пакет.

Наш проект будет иметь следующую функциональность:

- Метод возвращающий строку: "Hello World!";
- Команда `helloworld` печатающая эту строку в стандартный вывод.

.. note:: Исходные коды для данной статьи можно увидеть по адресу: https://github.com/klen/klen.github.com/tree/master/_code/helloworld-project


Создаем структуру проекта
=========================

Для начала создадим директорию для пакета. Ее минимальный
набор файлов состоит из: файла дистрибьюции (`setup.py`) описывающего
метаданные и python кода проекта (в нашем случае модуля ``helloworld``).

Также, xорошим тоном считается создание в корне директории файла с описанием проекта: `README.txt`.

Получаем следующую структуру: ::

    helloworld-project
    ├── helloworld
    │   ├── __init__.py
    │   └── core.py
    ├── setup.py
    └── README.txt

Наша корневая директория `helloworld-project` будет содержать мета-данные пакета и вспомогательные файлы
(тесты, лицензию, документацию и т.д.), а поддиректория `helloworld` непосредственно сам модуль `helloworld`.

Теперь отредактируем файл: `helloworld/core.py` и добавим логику нашего приложения (получение и вывод строки "Hello World!"):

.. code-block:: python

    def get_message():
        return "Hello World!"


    def print_message():
        print get_message()


Редактируем мета-информацию (setup.py)
======================================

Заполним файл описания `README.rst`: 

.. code-block:: rst

    Description
    ===========

    An example Hello World project.

Теперь отредактируем файл `setup.py`:

.. code-block:: python

    from setuptools import setup, find_packages
    from os.path import join, dirname

    setup(
        name='helloworld',
        version='1.0',
        packages=find_packages(),
        long_description=open(join(dirname(__file__), 'README.txt')).read(),
    )

.. note:: Убедитесь, что в вашей системе доступны setuptools_, в противном
    случае установите python-пакет distribute_

Этих операций достаточно, чтобы собрать пакет дистрибьюции. Выполните команду
сборки:

.. code-block:: shell

    $ python setup.py sdist

В случае успеха вы получите файл: `dist/helloworld-1.0.tar.gz`. Это полноценный,
архивированный python-пакет и вы можете распространять его среди прочих разработчиков.


Виртуальное окружение
=====================

Virtualenv_ — пакет применяемый для создания изолированного python-окружения. Используем
его для тестирования нашего проекта.

Создадим окружение ``env``:

.. code-block:: shell

    $ virtualenv env

Команда создаст директорию ``env`` внутри нашего проекта и установит туда ``python``, ``pip`` и ``distribute``.
Произведем в него установку нашего проекта.

.. code-block:: shell

    $ ./env/bin/python setup.py install
    running install
    running bdist_egg
    running egg_info
    [...]
    Processing dependencies for helloworld==1.0
    Finished processing dependencies for helloworld==1.0

И протестируем его работоспособность:

.. code-block:: shell

    $ ./env/bin/python
    >>> import helloworld.core as hw
    >>> hw.get_message()
    'Hello World!'
    >>> hw.print_message()
    Hello World!

Все работает. Осталось добавить поддержку команды ``helloworld`` в консоли.


Создание команд
===============

Для создания команды ``helloworld`` изменим файл `setup.py`:

.. code-block:: python

    setup(
        ...
        entry_points={
            'console_scripts':
                ['helloworld = helloworld.core:print_message']
            }
        )

В параметре ``entry_points`` мы задаем словарь с "точками вызова" нашего приложения. Ключ ``console_scripts``
задает список создаваемых исполняемых скриптов (в Windows это будут exe-файлы). В данном случае
мы указали создание исполняемого скрипта ``helloworld`` при вызове которого будет запускаться метод ``print_message``
из модуля ``helloworld.core``.

Переустановим модуль в наше окружение и проверим работу созданного скрипта (для этого прийдется активировать наше окружение):

.. code-block:: shell

    $ ./env/bin/python setup.py install
    $ source ./env/bin/activate
    (env)
    $ helloworld
    Hello World!
    (env)

Похоже все работает.


Работа с версиями
=================

Номер версии важная часть любого проекта. От него зависит обновление пакетов
и разрешение зависимостей. В примере выше мы указали номер версии ``1.0`` в файле `setup.py`.
Более правильное решение перенести его в файл `helloworld/__init__.py` чтобы сделать доступным
в python-коде. По существующим соглашения для хранения номера версии в модуле, используется
переменная ``__version__``.

`helloworld/__init__.py``:

.. code-block:: python

    __version__ = '1.0'

Изменим файл `setup.py`, чтобы нам не приходилось редактировать номер версии в двух местах:

.. code-block:: python

    ...
    import helloworld

    setup(
        name='helloworld',
        version=helloworld.__version__,
        ...

Существует множество систем наименования версий в python обычно рекомендуется использовать PEP386_.
Можно представить, что обозначение версии состоит из номера мажорного, минорного релизов
(номера багфикса при необходимости), разделенных точками. В последней части версии
разрешается использовать буквы латинского алфавита. Примеры из официальной документации: ::

    0.4       0.4.0  (these two are equivalent)
    0.4.1
    0.5a1
    0.5b3
    0.5
    0.9.6
    1.0
    1.0.4a3
    1.0.4b1
    1.0.4


Управление зависимостями
========================

Добавим функциональности нашему проекту. Создадим команду ``serve`` которая будет запускать
вебсервер отдающий страницу со строкой "Hello world!" генерируемой нашим модулем. Для этого
воспользуемся пакетом Flask_.

Добавляем файл `helloworld/web.py`:

.. code-block:: python

    from flask import Flask, render_template

    from helloworld.core import get_message


    app = Flask(__name__)


    @app.route("/")
    def hello():
        return render_template('index.html',
            message=get_message())


    def run_server():
        app.run()

И файл `helloworld/templates/index.html`:

.. code-block:: html

    <!DOCTYPE HTML>
    <body>{{message}}</body>

И опишем команду ``serve`` в файле `setup.py`:

.. code-block:: python

     ...
     entry_points={
        'console_scripts': [
            'helloworld = helloworld.core:print_message',
            'serve = helloworld.web:run_server',
            ]
        },
     ...

Теперь в нашем проекте появилась зависимость от пакета Flask_. Без его установки наше приложение
не будет правильно работать. За описание зависимостей в файле `setup.py` отвечает параметр ``install_requires``:

.. code-block:: python

    ...
    install_requires=[
        'Flask==0.8'
    ]

Проверим установку зависимостей обновив наш пакет и работу команды ``serve``:

.. code-block:: shell

    $ ./env/bin/python setup.py develop
    ...
    Processing dependencies for helloworld==0.1
    Searching for Flask==0.8
    ...
    $ serve
       * Running on http://127.0.0.1:5000/

Открыв браузер по адресу ``http://127.0.0.1:5000`` вы должны увидеть нашу страницу.


Управление файлами проекта (MANIFEST.in)
========================================

На текущий момент при сборке нашего пакета ``distutils`` включает в него только python-файлы.
Необходимо включить в него файл `helloworld/templates/index.html` без которого проект работать не будет.

Чтобы сделать это мы должны сообщить ``distutils`` какие еще файлы надо включать в наш проект. Один из способов —
это создание файла `MANIFEST.in`:

.. code-block:: shell

    recursive-include helloworld/templates *.html


Данная команда указывает ``distutils`` на включение в проект *всех* html файлов в директории `helloworld/templates`. 

Также придется обновить `setup.py`:

.. code-block:: python

    ...
    setup(
        ...
        include_package_data=True,
        ...
        )

Теперь шаблоны будут включены в наш проект.


Создание и запуск тестов
========================

Хорошей практикой считается создание тестов для вашего проекта.
Добавим простейшую реализацию, файл `tests.py`:

.. code-block:: python 

    from unittest import TestCase
    from helloworld.core import get_message

    class HelloworldTestCase(TestCase):
        def test_helloworld(self):
            self.assertEqual(get_message(), 'Hello World!')

И обновим `setup.py`:

.. code-block:: python 

    ...
    setup(
        ...
        test_suite='tests',
        ...
        )

Теперь мы можем произвести предварительное тестирование нашего проекта:

.. code-block:: shell 

    $ python setup.py test
    running test
    running egg_info
    writing requirements to helloworld.egg-info/requires.txt
    writing helloworld.egg-info/PKG-INFO
    writing top-level names to helloworld.egg-info/top_level.txt
    writing dependency_links to helloworld.egg-info/dependency_links.txt
    writing entry points to helloworld.egg-info/entry_points.txt
    reading manifest file 'helloworld.egg-info/SOURCES.txt'
    reading manifest template 'MANIFEST.in'
    writing manifest file 'helloworld.egg-info/SOURCES.txt'
    running build_ext
    test_helloworld (tests.HelloworldTestCase) ... ok

    ----------------------------------------------------------------------
    Ran 1 test in 0.000s

    OK

Обратите внимание, что для запуска тестов даже не нужно создание виртуального окружения. Необходимые
зависимости будут скачаны в директорию проекта в виде ``egg`` пакетов.


Публикация пакета на pypi.python.org
====================================

Прежде чем вы сможете опубликовать свой проект вам необходимо зарегистрироваться на PyPi_.
Запишите ваши реквизиты в файле `~/.pypirc`:

.. code-block:: shell 

    [distutils]
    index-servers =
        pypi

    [pypi]
    username:<username>
    password:<password>

Все ваш проект готов к публикации. Достаточно ввести соответствующую команду: 

.. code-block:: shell 

    $ python setup.py register sdist upload

.. note:: Вы не сможете опубликовать пакет `helloworld`, тк данное имя проекта уже занято.


.. _Python: http://python.org
.. _Virtualenv: http://pypi.python.org/pypi/virtualenv/
.. _setuptools: http://pypi.python.org/pypi/setuptools
.. _distutils: http://docs.python.org/distutils/
.. _distribute: http://pypi.python.org/pypi/distribute
.. _REST: http://docutils.sourceforge.net/rst.html
.. _PEP386: http://www.python.org/dev/peps/pep-0386/
.. _Flask: http://pypi.python.org/pypi/Flask/0.8
.. _PyPi: http://pypi.python.org
