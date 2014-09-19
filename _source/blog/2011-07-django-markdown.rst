Django-markdown — поддержка Markdown в Django
#############################################

:category: Blog
:date: 2011-07-09
:lang: ru
:slug: git-markdown
:tags: python, markdown, django

----

.. contents:: Содержание:

----

.. note::
    Markdown_ (маркдаун) — облегчённый язык разметки. Первоначально создан
    Джоном Грубером (англ. John Gruber) и Аароном Шварцем, целью которых
    являлось создание максимально удобочитаемого и удобного в публикации
    облегчённого языка разметки. Многие идеи языка были позаимствованы из
    существующих соглашений по разметке текста в электронных письмах. 
    Реализации языка Markdown преобразуют текст в формате Markdown в валидный,
    правильно построенный XHTML и заменяет левые угловые скобки («<») и
    амперсанды («&») на соответствующие коды сущностей.

Иногда возникает необходимость использовать язык разметки для редактирования
текстов. HTML редактировать руками при набивании текстов никто не хочет да это
и не нужно, а вот какой нибудь wiki-синтаксис или Markdown_ интуитивно понятны
программистам. Конечно секретаршу трудно обучить не GUI-евой разметке (хотя
возможно), но если проект предполагает нечастые обновления силами
квалифицированного персонала, Markdown_ становится очень удобен.

Для своих задач я написал Django-markdown_ — Django_ приложение позволяющее
быстро и несложно подключить Markdown_ синтаксис на проект.

Список возможностей:

- Поддержка Markdown_ синтаксиса в шаблонах;
- Поддержка в стандартных Django-flatpages_;
- Поддержка в стандартном Django-admin_;
- Поддержка в формах и виджетах (wysiwyg).

.. image:: /static/img/django-markdown.jpg


Чаще всего я использую это приложение, когда на проекте есть Django-flatpages_
для удобства редактирования.

.. note::
    Django-markdown_ предназначен для версии Django 1.3 и выше.


Установка
=========

Приложение можно установить из PyPi_

.. code-block:: bash

    easy_install django-markdown

    # Или с помощью pip

    pip install django-markdown


Подключение к проекту
=====================

Необходимо добавить `django_markdown` в **INSTALLED_APPS**, settings.py:

.. code-block:: python

    INSTALLED_APPS += 'django_markdown',

И создать url в базовом url_config, urls.py:

.. code-block:: python

    url('^markdown/', include( 'django_markdown.urls')),

.. note::
    Подключать URL необходимо если вы хотите использовать функционал
    предпросмотра в виджетах.


Использование и настройка
=========================

1. Использование в формах:

.. code-block:: python

    from django_markdown.widgets import MarkdownWidget

    class MyMarkdownForm(forms.Form):
        content = forms.CharField( widget=MarkdownWidget() )

.. note::
    Просто подключаем виджет к нужному полю.

2. В стандартном Django-admin_:

.. code-block:: python

    from django_markdown.admin import MarkdownModelAdmin

    adimin.site.register(MyModel, MarkdownModelAdmin)

.. note::
    Все поля типа TextField будут выведены с использованием Markdown_ виджета

3. Django-flatpages_:

.. code-block:: python

    # В вашем базовом url_config
    from django_markdown import flatpages

    ... URLS ..

    # Setup django admin and flatpages
    admin.autodiscover()
    flatpages.register()
    urlpatterns += [ url(r'^admin/', include(admin.site.urls)), ]

.. note::
    Мы импортируем flatpages из django_markdown вместо стандартного пути.

4. Настройка скинов wysiwyg (markitup по-умолчанию) settings.py:

.. code-block:: python

    MARKDOWN_EDITOR_SKIN = 'simple'

.. note::
    Подробнее про настройку скинов и JS API читайте на сайте Markitup_


Надеюсь это приложение и синтаксис будут вам полезны.


.. _Markdown: http://ru.wikipedia.org/wiki/Markdown
.. _Django: http://django-project.com
.. _Django-markdown: https://github.com/klen/django_markdown
.. _Django-flatpages: https://docs.djangoproject.com/en/dev/ref/contrib/flatpages/
.. _Django-admin: https://docs.djangoproject.com/en/dev/ref/contrib/admin/
.. _Markitup: http://markitup.jaysalvat.com/home/
.. _PyPi: http://pypi.python.org

