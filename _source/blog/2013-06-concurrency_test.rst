Ускорение python тестов. Конкурентный запуск.
#############################################

:category: Blog
:date: 2013-06-11
:lang: ru
:slug: concurrency-tests
:tags: python,test,django

----

.. contents:: Содержание:

----

Прогон тестов на большом проекте отнимает продолжительное время. Простейший
способ ускорить выполнение на многоядерной системе использовать конкуренцию.


Nose
====

Если вы используете nose_ для тестирования, то у вас уже есть возможность
конкурентного запуска.

    "You can parallelize a test run across a configurable number of worker
    processes. While this can speed up CPU-bound test runs, it is mainly useful
    for IO-bound tests that spend most of their time waiting for data to arrive
    from someplace else and can benefit from parallelization."

    -- nose_


Обычный запуск тестов выглядит так: ::

    $ nosetests


Для использования конкуренции: ::

    $ nosetests --processes=4


Unittest
========

Все хорошо, но как ускорить тесты если вы не используете nose_? Задавшись этим
вопросом я обнаружил модуль concurrencytest_ от `Corey Goldberg`_. Он позволяет
переопределить ``unittest.TestSuite`` для использования конкурентного запуска
тестов.

Базовый пример использования: ::

    from concurrencytest import ConcurrentTestSuite, fork_for_tests

    # Здесь мы определяем unittest.TestSuite и unittest.TestRunner
    suite = ...

    # И обеспечиваем конкурентный запуск
    concurrent_suite = ConcurrentTestSuite(suite, fork_for_tests())
    runner.run(concurrent_suite) 

Вот и все. Теперь тесты будут выполняться асинхронно.

.. note:: По умолчанию concurrencytest_ запускает форки по количеству ядер
          процессора вашей системы. Вы можете явно указать количество процессов
          при создании ConcurrentTestSuite задав аргумент для функции для
          fork_for_tests (fork_for_tests(8)).


Django
------

Приведу пример интеграции concurrencytest_ в Django_ проект. Нужно создать
собственный `TestRunner` который переопределит создаваемую `TestSuite`.
Пусть код проекта лежит в модуле `main`, создадим файл `main/test_runner.py`::


    from concurrencytest import ConcurrentTestSuite, fork_for_tests
    from django.test.simple import DjangoTestSuiteRunner


    class DjangoConcurencyTestSuiteRunner(DjangoTestSuiteRunner):

        def build_suite(self, test_labels, extra_tests=None, **kwargs):
            suite = super(DjangoConcurencyTestSuiteRunner, self).build_suite(
                test_labels, extra_tests=extra_tests, **kwargs
            )

            concurrency_suite = ConcurrentTestSuite(suite, fork_for_tests())
            return concurrency_suite


Теперь осталось переопределить опцию ``TEST_RUNNER`` в настройках  Django_,
указав путь импорта к нашему раннеру: ::

    TEST_RUNNER = 'main.test_runner.DjangoConcurencyTestSuiteRunner'


Не забудьте добавить в ваше окружение зависимость от concurrencytest_ и
обновить его.

Все, теперь запуск Django тестов будет автоматически использовать
все присуствующие в системе ядра процессора. В моих проектах прирост скорости
выполнения тестов составил от 35% до 60% процентов, на 4-х ядерном macbook pro.


.. note:: Кстати если вы используете tox_ для прогона тестов используя разные
    окружения, то для использования конкурентного запуска вам достаточно
    просто установить модуль detox_ и запускать tox-тесты с его помощью.


.. _Django: http://djangoproject.org/
.. _nose: https://nose.readthedocs.org/en/latest/
.. _concurrencytest: https://github.com/cgoldberg/concurrencytest.git
.. _`Corey Goldberg`: http://goldb.org/
.. _tox: https://pypi.python.org/pypi/tox/
.. _detox: https://pypi.python.org/pypi/detox/
