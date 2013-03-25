Неделя с Flask
##############

:category: Blog
:date: 2012-08-31
:lang: ru
:slug: some-flask-things
:tags: python,flask,sqlalchemy

----

.. contents:: Содержание:

----

Стал использовать Flask_ для небольших проектов. Django_ неимоверно разрослась,
да и просто замылила глаз. В процессе работы родилось несколько полезных приложений.


Flask-Foundation
================

Я `уже писал <../notes-flask-opensource-ru.html>`_ про open-source проекты на Flask_ с хорошим исходным кодом.
Но как показывает практика, для быстрого старта их недостаточно.

Я собрал свою сборку: http://github.com/klen/Flask-Foundation базового
проекта на Flask_, содержащую следующие вещи:

* `Flask-Admin`_ — администрирование;
* `Flask-Script`_ — автоматизация;
* `Flask-Cache`_ — кеширование;
* `Flask-Debugtoolbar`_ — отладка;
* `Flask-Babel`_ — локализация;
* `Flask-WTF`_ — поддержка WTForms;
* `Flask-Bootstrap`_ — стилизация;
* `Flask-Mail`_ — почта;
* `Flask-SQLAlchemy`_ — ORM, базы данных;
* `Flask-Testing`_ — тестирование;
* `Alembic`_ — миграции бд;

Проект содержит богатый функционал и может послужить хорошим примером для быстрого старта.


Flask-Mixer
===========

Фабрика генерации объектов из SQLAlchemy_ моделей. Создавалась мной в целях тестирования,
но может использоваться и в других случаях (пакетная генерация данных).

Адрес на Github_: http://github.com/klen/Flask-Mixer

Примеры работы:

.. code-block:: python 

            # Простая генерация модели
            user1 = mixer.blend(User)
            assert user1.id and user1.username and user1.created_at
            assert user1.score == 50
            assert user.profile.user == user

            # Модель может быть задана строкой
            role1 = mixer.blend('app.models.Role')
            assert role1.user
            assert role1.user_id == role1.user.id

            # Генерация объекта с предопределенными значениями
            user2 = mixer.blend(User, username='test')
            assert user2.username == 'test'

            # Это могут быть значения для референс-объектов
            role1 = mixer.blend(Role, user__username='test2')
            assert role2.user.username == 'test2'

            # Значение может быть функцией
            user = mixer.blend(User, username=lambda:'callable_value')
            assert user.username == 'callable_value'

            # Принудительная установка случайного значения для поля с default value
            user = mixer.blend(User, score=mixer.random)
            assert user.score != 50

            # Установка случайного значения из базы данных
            profiles = Profile.query.all()
            user = mixer.blend(User, profile=mixer.random)
            assert user.profile in profiles


Flask-Collect
=============

Нехватку такого приложения я почувствовал при первом же деплое Flask_-проекта.
Как известно раздавать статичные файлы (css, js и тп) питоном в нашем
бизнесе не комильфо. Обычно проксирующий WSGI веб-сервер отдает их
из определенной папки напрямую. Для сборки таких файлов из приложений проекта
в Django_ существует встроенное приложение.

Во Flask_ ничего подобного не нашлось. Есть инструкции в документации где
рекомендовано отдавать статичные файлы веб-сервером, но нет ни слова о том
как их собирать. Не найдя ничего на Pypi я написал свое.

Использование:

В коде:

.. code-block:: python 

    app = Flask(__name__)
    collect = Collect(app)
    collect.collect(verbose=True)

или из консоли при использовании `Flask-Script`_:

.. code-block:: shell 

    $ ./manage.py collect

Адрес на Github_: http://github.com/klen/Flask-Collect


Заключение
==========

В целом Flask_ мне нравится. Код чище, его меньше, работает быстрее.
SQLAlchemy_ на голову уделывает на текущий момент Django_ ORM.

Но порог вхождения гораздо выше, как ни странно, множество задач уже
решенных сообществом Django_ тут приходится решать заново.


.. _Flask: http://flask.pocoo.org/
.. _Flask-Admin: https://github.com/mrjoes/flask-admin/
.. _Flask-Script: http://github.com/rduplain/flask-script
.. _Flask-Cache: http://packages.python.org/Flask-Cache/
.. _Flask-Debugtoolbar: http://flask.pocoo.org/docs/extensiondev/
.. _Flask-Babel: http://github.com/mitsuhiko/flask-babel
.. _Flask-WTF: http://github.com/rduplan/flask-wtf
.. _Flask-Bootstrap: http://github.com/mbr/flask-bootstrap
.. _Flask-Mail: http://packages.python.org/Flask-Mail/
.. _Flask-SQLAlchemy: http://github.com/mitsuhiko/flask-sqlalchemy
.. _Flask-Testing: http://packages.python.org/Flask-Testing/
.. _Github: http://github.com
.. _Django: http://djangoproject.org/
.. _Alembic: http://pypi.python.org/pypi/alembic/0.3.5
.. _SQLAlchemy: http://www.sqlalchemy.org/
