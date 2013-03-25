Несколько полезных сниппетов для джанго
#######################################

:category: Blog
:date: 2011-12-02
:lang: ru
:slug: django-snippets
:tags: python, django, cache, upload, orm

----

.. contents:: Содержание:

----

Ниже находится несколько полезных Django_ сниппетов, которые я использую в своей работе.


Автоматическая генерация имени файла в полях типа FileField, ImageField
=======================================================================

В Django_ поля типа FileField_ и ImageField_ позволяют определять функцию для генерации имени
сохраняемого файла. Она указывается в аргументе ``upload_to`` при создании поля.

Когда мне надоело придумывать уникальные имена файлов, при сохранении их
в Django_-проектах я написал нижеприведенный сниппет.

- Генерируемые пути файлов содержат только латинские и цифровые символы;
- Файлы с одинаковыми названиями, загружаемые в разные инстансы не перезаписываются;
- Файлы удобно хранятся отсортированные по приложениям и моделям;
- Путь файла однозначно говорит нам о том, что за инстанс его использует;
- Система не позволяет тысячам файлов скапливаться в одной папке;

.. code-block:: python

    from hashlib import md5
    from os import path as op
    from time import time


    def upload_to(instance, filename, prefix=None, unique=False):
        """ Auto generate name for File and Image fields.
        """
        ext = op.splitext(filename)[1]
        name = str(instance.pk or '') + filename + (str(time()) if unique else '')

        # We think that we use utf8 based OS file system
        filename = md5(name.encode('utf8')).hexdigest() + ext
        basedir = op.join(instance._meta.app_label, instance._meta.module_name)
        if prefix:
            basedir = op.join(basedir, prefix)
        return op.join(basedir, filename[:2], filename[2:4], filename)


Пример работы
-------------

Например у нас есть модель ``Archive`` в приложении ``storage``, `storage/models.py`:

.. code-block:: python

    from django.db import models

    class Archive(model.Model):
        title = models.CharField(max_length=100)
        file = models.FileField(upload_to=upload_to)

В результате сохраненные файлы будут иметь пути вида:
`{MEDIA_URL}/storage/archive/21/40/2140e8fe8678bc08ff6e9b10c9639068.zip`

Здесь присутствует имя приложения, имя модели, созданное новое имя файла и его расширение.
При этом путь дробится на папки согласно четырем первым символам в имени файла `21/40/2140e8...`.
Это позволяет значительно отсрочить ситуацию с сотнями тысяч объектов в папке и тормоза файловой системы.

Параметры сниппета
------------------

Функция `upload_to` может принимать до 4-х параметров. Аргументы **instance** и **filename** передаются Django_.

Аргумент **prefix** принимает строковые значения и позволяет дополнительно настраивать пути файлов.
Например при определении префикса `prefix="cart"` вышеприведенный код будет сохранять файлы с путями вида: 
`{MEDIA_URL}/storage/archive/cart/21/40/2140e8fe8678bc08ff6e9b10c9639068.zip`. Префикс был добавлен после имени модели.

Аргумент **unique** принимает булевы значения и позволяет гарантированно получить уникальное имя файла. По-умолчанию для `instance`
с одинаковым ключом, для одинаковых имен файла, будет создан идентичный путь. Это сделано намеренно, чтобы при обновлении
файлов пути в конкретной модели не изменялись. Параметр `unique` меняет это поведение и при каждом изменении файла, путь будет другим.

Но как использовать все эти параметры если Django_ передает в указанную функцию только первые два? Здесь нам поможет Каррирование_.
Мы используем функцию **curry** из `django.utils.functional`, которая имитирует это поведение в python.

Например в нижеприведенном коде:

.. code-block:: python

    from django.db import models
    from django.utils.functional import curry

    class Archive(model.Model):
        title = models.CharField(max_length=100)
        cover = models.ImageField(upload_to=curry(upload_to, prefix='cover'))
        file = models.FileField(upload_to=curry(upload_to, prefix='file'))
        other = models.FileField(upload_to=curry(upload_to, unique=True))

Файлы из поля `cover` будут сохраняться с путями вида: `{MEDIA_URL}/storage/archive/cover/21/40/2140e8fe8678bc08ff6e9b10c9639068.jpg`

Файлы из поля `file` будут сохраняться с путями вида: `{MEDIA_URL}/storage/archive/file/21/40/2140e8fe8678bc08ff6e9b10c9639068.zip`

Файлы из поля `other` всегда будут иметь уникальные пути, вида: `{MEDIA_URL}/storage/archive/11/11/1111e8fe8678bc08ff6e9b10c9639068.mp3`


Работа с кешем
==============

В работе с кешированием проекта нужна четкая стратегия и обозначенные соглашения.
Например наименования ключей кэша. `SomeModel.object.filter(active=True)` с каким ключом хранить
результат выполнения этого запроса? Как параллельный разработчик узнает этот ключ? Когда производить
инвалидацию? Для Django_ существуют приложения помогающие решать эту проблему, но зачастую они слишком
перегружены и сложны в использовании.

Для простых проектов я написал несколько полезных функций:

.. code-block:: python

    import hashlib
    import re

    from django.core.cache import cache
    from django.db.models import Model, get_model
    from django.db.models.base import ModelBase
    from django.db.models.query import QuerySet
    from django.utils.encoding import smart_str

    def cached_instance(model, **filters):
        """ Auto cached model instance.
        """
        if isinstance(model, basestring):
            assert '.' in model, ("'model_class' must be either a model"
                                    " or a model name in the format"
                                    " app_label.model_name")
            app_label, model_name = model.split(".")
            model = get_model(app_label, model_name)

        cache_key = generate_cache_key(model, **filters)
        return get_cached(cache_key, model.objects.select_related().get, kwargs=filters)


    def cached_query(qs, timeout=None):
        """ Auto cached queryset and generate results.
        """
        cache_key = generate_cache_key(qs)
        return get_cached(cache_key, list, args=(qs,), timeout=None)


    def clean_cache(*args, **kwargs):
        """ Generate cache key and clean cached value.
        """
        cache_key = generate_cache_key(*args, **kwargs)
        cache.delete(cache_key)


    def generate_cache_key(cached, **kwargs):
        """ Auto generate cache key for model or queryset
        """
        if isinstance(cached, QuerySet):
            key = str(cached.query)

        elif isinstance(cached, (Model, ModelBase)):
            key = '%s.%s:%s' % (cached._meta.app_label,
                    cached._meta.module_name,
                    ','.join('%s=%s' % item for item in kwargs.iteritems()))

        else:
            raise AttributeError("Objects must be queryset or model.")

        if not key:
            raise Exception('Cache key cannot be empty.')

        key = clean_cache_key(key)
        return key


    def clean_cache_key(key):
        """ Replace spaces with '-' and hash if length is greater than 250.
        """
        cache_key = re.sub(r'\s+', '-', key)
        cache_key = smart_str(cache_key)

        if len(cache_key) > 200:
            cache_key = cache_key[:150] + '-' + hashlib.md5(cache_key).hexdigest()

        return cache_key


    def get_cached(cache_key, func, timeout=None, args=None, kwargs=None):
        args = args or list()
        kwargs = kwargs or dict()
        result = cache.get(cache_key)

        if result is None:

            if timeout is None:
                timeout = cache.default_timeout

            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)

        return result

        #**

Примеры работы
--------------

.. code-block:: python

    # Генерация ключей для Queryset (разные ключи для разных запросов)
    print generate_cache_key(TaxiStation.objects.all())
    print generate_cache_key(TaxiStation.objects.all())
    print generate_cache_key(TaxiStation.objects.filter(active=True))
    print generate_cache_key(TaxiStation.objects.filter(city=1, title="intaxi"))
    print generate_cache_key(TaxiStation.objects.filter(active=True))

    # Output: 'SELECT-"main_taxistation"."id",-"main_taxistation"."active",-"main_taxistation"."title",-"main_taxistation"."city_id",-"main_taxistation"."agent_id",--873aa3b2fbd81cdaa9fce75e60706579'
    # Output: 'SELECT-"main_taxistation"."id",-"main_taxistation"."active",-"main_taxistation"."title",-"main_taxistation"."city_id",-"main_taxistation"."agent_id",--873aa3b2fbd81cdaa9fce75e60706579'
    # Output: 'SELECT-"main_taxistation"."id",-"main_taxistation"."active",-"main_taxistation"."title",-"main_taxistation"."city_id",-"main_taxistation"."agent_id",--043271300c8db6cc9152ef3119e6195c'
    # Output: 'SELECT-"main_taxistation"."id",-"main_taxistation"."active",-"main_taxistation"."title",-"main_taxistation"."city_id",-"main_taxistation"."agent_id",--98960ebe77c30e08fe6b4a4fd2b1ab57'
    # Output: 'SELECT-"main_taxistation"."id",-"main_taxistation"."active",-"main_taxistation"."title",-"main_taxistation"."city_id",-"main_taxistation"."agent_id",--043271300c8db6cc9152ef3119e6195c'

    # Генерация ключей для Model
    print generate_cache_key(TaxiStation, pk=100, active=True)
    print generate_cache_key(TaxiStation, pk=50)

    # Output: main.taxistation:pk=50

    # Кеширование Queryset (получение данных из кеша или из БД с сохранением в кеш)
    all = cached_query(SomeModel.objects.all())
    some_results =  cached_query(SomeModel.objects.filter(param=True))

    # Принудительная очистка кеша Queryset
    clean_cache(SomeModel.objects.all())
    clean_cache(SomeModel.objects.filter(param=True))

    # Кеширование instance
    order = cached_instance(Order, pk=20, title="Some title")

    # можно и по имени
    order = cached_instance('app.order', pk=20, title="Some title")

    # Очистка кеша
    clean_cache(Order, pk=20, title="Some title")


Атомарные обновления
====================

Часто возникают ситуации когда нам необходимо обновить одно или несколько полей объекта.
В Django_ по-умолчанию это можно сделать при помощи следующего кода:

.. code-block:: python

    # Допустим у нас есть объект order (instance of model)
    order.custom_field = custom_value
    order.full_clean()
    order.save()

При этом ORM Django_ создает и выполняет запрос содержащий обновление **всех полей** объекта, что может быть довольно медленной операцией.

Значительно быстрее сработает следующая конструкция:

.. code-block:: python

    order.custom_field = custom_value
    order.full_clean()
    Order.objects.filter(pk=order.pk).update(custom_field = custom_value)

Но она несколько неудобна. Следующая функция решает эту проблему.

.. code-block:: python

    import operator

    from django.db import models
    from django.db.models.expressions import F, ExpressionNode


    EXPRESSION_NODE_CALLBACKS = {
        ExpressionNode.ADD: operator.add,
        ExpressionNode.SUB: operator.sub,
        ExpressionNode.MUL: operator.mul,
        ExpressionNode.DIV: operator.div,
        ExpressionNode.MOD: operator.mod,
        ExpressionNode.AND: operator.and_,
        ExpressionNode.OR: operator.or_,
        }

    class CannotResolve(Exception):
        pass

    def _resolve(instance, node):
        if isinstance(node, F):
            return getattr(instance, node.name)
        elif isinstance(node, ExpressionNode):
            return _resolve(instance, node)
        return node

    def resolve_expression_node(instance, node):
        op = EXPRESSION_NODE_CALLBACKS.get(node.connector, None)
        if not op:
            raise CannotResolve
        runner = _resolve(instance, node.children[0])
        for n in node.children[1:]:
            runner = op(runner, _resolve(instance, n))
        return runner

    def update(instance, full_clean=False, **kwargs):
        "Atomically update instance, setting field/value pairs from kwargs"

        # apply the updated args to the instance to mimic the change
        # note that these might slightly differ from the true database values
        # as the DB could have been updated by another thread. callers should
        # retrieve a new copy of the object if up-to-date values are required
        for k, v in kwargs.iteritems():
            if isinstance(v, ExpressionNode):
                v = resolve_expression_node(instance, v)
            setattr(instance, k, v)

        # clean instance before update
        if full_clean:
            instance.full_clean()

        # fields that use auto_now=True should be updated corrected, too!
        for field in instance._meta.fields:
            if hasattr(field, 'auto_now') and field.auto_now and field.name not in kwargs:
                kwargs[field.name] = field.pre_save(instance, False)

        rows_affected = instance.__class__._default_manager.filter(pk=instance.pk).update(**kwargs)
        return rows_affected

    #**

Теперь мы можем делать так:

.. code-block:: python

    # Обновили объект и сохранили его в базу, через
    update(order, custom_field=custom_value)

    print order.custom_field
    # Output: custom_value

Или даже так:

.. code-block:: python

    update(order, custom_field=custom_value, other_field=other_value, more_field=more_value)

Обходясь при этом без тяжелых запросов к базе.

::

    SELECT (1) AS "a" FROM "main_order" WHERE "main_order"."id" = 22387  LIMIT 1; args=(22387,)
    UPDATE "main_order" SET "created_at" = E'2011-12-02 19:39:00.969044', "city_id" = 1, "when" = E'2011-12-02 19:50:00', "price" = E'100.00', "expected_price" = E'350.00', "car_class" = 10, "conditioner" = false, "smoke" = false, "no_smoke" = false, "child_seat" = false, "long_length" = false, "meet_sign" = false, "from_address_id" = 17130, "to_address_id" = 17131, "route_id" = NULL, "from_node_id" = 501, "to_node_id" = 501, "from_address_entrance_no" = E'', "from_comment" = E'', "to_comment" = E'', "flight_number" = E'', "meet_sign_text" = E'', "auto_id" = NULL, "fare_id" = 42, "taxistation_id" = 1, "passenger_id" = 71111111111, "device_id" = E'200774696189910', "device_agent" = E'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.2 ', "device_name" = E'Web', "device_token" = E'', "device_sms" = true, "current_status" = E'WaitForCarAssigment', "updated" = E'2011-12-02 19:40:09.405462', "credit" = false WHERE "main_order"."id" = 22387 ; args=(u'2011-12-02 19:39:00.969044', 1, u'2011-12-02 19:50:00', u'100.00', u'350.00', 10, False, False, False, False, False, False, 17130, 17131, 501, 501, u'', u'', u'', u'', u'', 42, 1, 71111111111L, u'200774696189910', u'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.2 ', u'Web', u'', True, 'WaitForCarAssigment', u'2011-12-02 19:40:09.405462', False, 22387)

VS ::

    UPDATE "main_order" SET "price" = E'100.00' WHERE "main_order"."id" = 22387 ; args=(u'100.00', 22387)


Надеюсь эти несколько простых функций, будут также полезны вам, как и мне.


.. _Django: http://djangoproject.com/
.. _FileField: https://docs.djangoproject.com/en/dev/ref/models/fields/#filefield
.. _ImageField: https://docs.djangoproject.com/en/dev/ref/models/fields/#imagefield
.. _Каррирование: http://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%80%D1%80%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5
