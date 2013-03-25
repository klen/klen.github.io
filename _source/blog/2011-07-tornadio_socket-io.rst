Создание сервера оповещений с использованием Tornado и Socket.IO
################################################################

:category: Blog
:date: 2011-07-06
:lang: ru
:slug: tornadio_socket-io
:tags: tornado, socketio, python, javascript

----

.. contents:: Содержание:

----

Структура современных веб-приложений зачастую включает в себя некие **HTTP API**
с которыми работают подключенные к серверу клиенты. Обычно для них важно
оперативно обновлять информацию о произошедших на сервере событиях.

.. note:: 
    Например оповещения о сообщениях в чатах, события в онлайн-играх,
    поступление новых заказов, предложений в системах коммерции и тп.

В данный момент на большинстве сайтов это реализуется постоянными **AJAX**
запросами к серверу с клиентской стороны.  У этого способа существуют
недостатки:

- Создается лишняя нагрузка на сервер;

- Информация может приходить с задержкой;

- Увеличивается трафик на клиенте.

В данной статье рассматривается способ с использованием WebSocket_ и Comet_
технологий. Мы создадим простейший сервер оповещений с использованием
SocketIO_ и Tornadio_. С клиентской стороны будет создаваться постоянное
подключение к нашему серверу и в нужный момент мы будем посылать оповещения
о событиях.

.. note::
    SocketIO_ — javascript библиотека предоставляющая единый интерфейс для
    связи с Comet_ сервером с использованием множества протоколов (WebSocket_,
    Flashsocket, XHR multipart и тд.).

	SocketIO_ уже поставляется с модулем для **nodejs**. С его помощью можно реализовать
	необходимую функциональность на сервере используя JavaScript_. В данной статье 
	рассматривается решение с использованием Python_.

.. note::
    Tornadio_ — python библиотека надстройка над Tornado_ для поддержки
    интерфейса SocketIO_.

.. note::
    Для дальнейшего чтения предполагается, что вы знакомы с Python_, VirtualEnv_ и
    JavaScript_.


Установка и настройка Tornadio
==============================

1. Для начала создадим и активируем виртуальное окружение (VirtualEnv_) для нашего сервера:

.. code-block:: bash

    # Создаем директорию для сервера
    mkdir -p ~/Projects/tornado_pushserver
    cd ~/Projects/tornado_pushserver

    # Создаем виртульное окружение
    virtualenv .ve

    # Активируем виртуальное окружение
    source .ve/bin/activate

2. Устанавливаем в созданное окружение Tornado_ и Tornadio_:

.. code-block:: bash

    easy_install tornadio


Создание приложения Tornado
===========================

1. Напишем обработчик HTTP подключений к нашему серверу. Создадим и
   отредактируем файл `handler.py`:

.. code-block:: python

    import tornado.web


    class BroadcastHandler(tornado.web.RequestHandler):

        def get(self):
            self.write('Hello from tornadio!')

Все, что он делает, это отдает строку 'Hello from tornadio!' при GET запросах.

2. Создадим основной файл приложения `app.py`

.. code-block:: python

    import tornado.web
    from tornadio import server

    from handler import BroadcastHandler


    urls = [ (r"/", BroadcastHandler) ]

    application = tornado.web.Application( urls )

    if __name__ == "__main__":
        server.SocketServer(application)

Здесь мы создали Tornado_ application использующее наш обработчик соединений.

.. note::
    Код для текущего состояния нашего сервера, вы можете посмотреть по адресу:
    https://github.com/klen/example_tornadio_project/tree/0.1.0

Запустите сервер с помощью команды `python app.py` и откройте в браузере
http://localhost:8001 вы должны увидеть ответ сервера. Если все в порядке
остановите его из консоли нажав Ctrl+C.


Клиентская часть
================

1. Создайте страницу для клиентов `console.html`:

.. code-block:: html

    <!DOCTYPE html>
    <html>
        <script src="http://cdn.socket.io/stable/socket.io.js"></script>
        <script>
            window.onload = function(){
                var log = document.getElementById('log');

                var socket = new io.Socket(window.location.hostname, {
                    port: 8001,
                    rememberTransport: false
                });

                socket.connect();

                socket.addEvent('message', function(data) {
                    log.innerHTML += '<p>' + data + '</p>';
                });
            };
        </script>
        <h2>Console client</h1>
        <div id='log'></div>
    </html>

Разберем, что в ней происходит. Подключается SocketIO_ скрипт реализации
протоколов. Создается объект `socket` с параметрами подключения к нашему
серверу. Происходит подключение `socket.connect`. И все полученные от сервера
сообщения выводятся в тело страницы.

2. Теперь подключим этот шаблон на стороне сервера, изменив `handler.py`:

.. code-block:: python

    class BroadcastHandler(tornado.web.RequestHandler):
        def get(self):
            self.render('console.html')

.. note::
    Код для текущего состояния нашего сервера, вы можете посмотреть по адресу:
    https://github.com/klen/example_tornadio_project/tree/0.2.0

Снова запустите сервер и подключитесь к нему в браузере: http://localhost:8001
Через какое то время в вы увидите ошибки в консоли. Они вызваны тем, что
протоколы SocketIO_ у нас сейчас никто не обрабатывает. Выключите сервер и
давайте создадим обработку подключений.


Обработка подключений
=====================

1. Создайте файл `connection.py`:

.. code-block:: python

    import logging
    from tornadio import SocketConnection


    class ClientConnection(SocketConnection):
        clients = set()
        def on_open(self, *args, **kwargs):
            logging.warning('client connected')
            self.clients.add(self)

        def on_close(self):
            logging.warning('client disconnected')
            self.clients.remove(self)

        # **

Здесь мы создали класс для наших подключений. При подключении он сохраняет
ссылку на себя в ClientConnection.client. При разрыве соединения удаляет.

2. Подключим его в наше приложение `app.py`:

.. code-block:: python

    import tornado.web
    from tornadio import server, get_router

    from connection import ClientConnection
    from handler import BroadcastHandler


    urls = [ (r"/", BroadcastHandler), get_router(ClientConnection).route() ]

    application = tornado.web.Application( urls )

    if __name__ == "__main__":
        server.SocketServer(application)

Сейчас мы создали ресурс SocketIO_ для клиентских подключений.

3. И доработаем на `handler.py` для отправки сообщений подключенным клиентам:

.. code-block:: python

    import tornado.web
    from connection import ClientConnection


    class BroadcastHandler(tornado.web.RequestHandler):

        def get(self):
            self.render('console.html')

        def post(self):
            message = self.get_argument('message')
            for client in ClientConnection.clients:
                client.send(message)
            self.write('message send.')

Мы добавили обработчик POST запросов, отправляющий сообщения нашим подключениям.

.. note::
    Код для текущего состояния нашего сервера, вы можете посмотреть по адресу:
    https://github.com/klen/example_tornadio_project/tree/0.3.0

Запустите сервер и откройте несколько страниц по адресу http://localhost:8001
В консоли сервера вы должны увидеть сообщения о подключении. Давайте попробуем
отправить сообщения подключенным клиентам с помощью POST запросов к нашему
серверу.

.. code-block:: bash

    curl localhost:8001 -d message=Ping
    curl localhost:8001 -d message=Another_ping

Вы должны увидеть как сообщения появляются на открытых страницах. Сейчас самый
простой вариант нашего сервера сообщений уже работает. Добавим в него
возможность посылать сообщения конкретным клиентам. Остановите сервер.


Идентификация подключений
=========================

Есть несколько вариантов идентифицировать клиент. Например можно запрашивать
пользовательскую сессию если она существует. Сейчас мы просто будем сообщать
случайно генерированный ID серверу после подключения. Доработаем немного
`console.html`:

.. code-block:: html

    <!DOCTYPE html>
    <html>
        <script src="http://cdn.socket.io/stable/socket.io.js"></script>
        <script>
            window.onload = function(){

                var log = document.getElementById('log');

                var socket = new io.Socket(window.location.hostname, {
                    port: 8001,
                    rememberTransport: false
                });

                // register client
                socket.addEvent('connect', function(e){
                    log.innerHTML += '<p>Connected.</p>';
                    socket.send({
                        id: Math.floor(Math.random(1000) * 1000)
                    });
                });

                socket.connect();

                socket.addEvent('message', function(data) {
                    log.innerHTML += '<p>' + data + '</p>';
                });
            };
        </script>
        <h2>Console client</h1>
        <div id='log'></div>
    </html>

Мы добавили реакцию на событие `connect` и отправляем на сервер информацию о
нашем текущем ID.

2. Добавим обработку идентификатора в наш класс подключений `connection.py`:

.. code-block:: python

    from tornadio import SocketConnection
    import logging


    class ClientConnection(SocketConnection):

        clients = set()

        def __init__(self, *args, **kwargs):
            self.id = None
            super(ClientConnection, self).__init__(*args, **kwargs)

        def on_open(self, *args, **kwargs):
            logging.warning('client connected')
            self.clients.add(self)

        def on_message(self, message):
            logging.warning(message)
            if not self.id:
                self.id = message.get('id', None)
            self.send('Hello client %s' % self.id)

        def on_close(self):
            logging.warning('client disconnected')
            self.clients.remove(self)

        # **

Теперь при получении сообщения, мы регистрируем идентификатор клиента.

3. И добавим функциональности в `handler.py`:

.. code-block:: python

    import tornado.web
    from connection import ClientConnection


    class BroadcastHandler(tornado.web.RequestHandler):

        def get(self):
            self.render('console.html')

        def post(self):
            message = self.get_argument('message')
            key = self.get_argument('id', None)
            for client in ClientConnection.clients:
                if key and not key == client.id:
                    continue
                client.send(message)
            self.write('message send.')

Сейчас мы проверяем запрос на наличие параметра id и в этом случае отправляем
сообщение только конкретному подключенному клиенту.

.. note::
    Код для текущего состояния нашего сервера, вы можете посмотреть по адресу:
    https://github.com/klen/example_tornadio_project/tree/0.4.0

Запустите сервер и откройте несколько соединений в браузере. Вы должны увидеть
сообщения о подключении и ответы сервера с зарегистрированными ID::

    Console client

    Connected.

    Hello client 63


Отправим несколько сообщений:

.. code-block:: bash

    curl localhost:8001 -d message=Hello_all
    curl localhost:8001 -d message=Hello_63&id=63

.. note::
    Во-втором сообщении подставьте ID для одного из своих подключений

Полученные сообщения должны отобразится в браузере. При чем первое для всех
подключенных соединений, а второе только для соединения с конкретным id.
Если все действительно так, то поздравляю ваш сервер сообщений работает.


Использование
=============

Итак сервер мы написали, каким образом его можно использовать?
Например запустить на другом порту вашего основного
домена и подключаться к нему с клиентских страниц. При этом если на основном
сервере происходит какое то событие, делается **POST** запрос (в идеале асинхронный)
к серверу оповещений который в свою очередь посылает сообщение клиенту.
В качестве сообщения можно отправлять **JSON** с необходимой информацией.

Но стоит учитывать, что данная статья является ознакомительной и
показывает создание **простейшего**
сервера. В нем нет защиты от возможности злоумышленника рассылать собственные
оповещения, не используются ресурсы SocketIO_, нет автоматических
пере-подключений с клиентской стороны при разрыве связи.

Это несложно реализовать и вы можете доработать сервер самостоятельно.

В заключении я рекомендую вам почитать документацию SocketIO_, Tornadio_ и возможно Tornado_.


.. _Comet: http://ru.wikipedia.org/wiki/Comet
.. _WebSocket: http://ru.wikipedia.org/wiki/WebSocket
.. _JSONP: http://en.wikipedia.org/wiki/JSONP
.. _SocketIO: http://socket.io/
.. _Tornado: http://tornadoweb.org
.. _Tornadio: https://github.com/MrJoes/tornadio
.. _VirtualEnv: http://pypi.python.org/pypi/virtualenv
.. _Python: http://python.org
.. _JavaScript: http://ru.wikipedia.org/wiki/JavaScript
