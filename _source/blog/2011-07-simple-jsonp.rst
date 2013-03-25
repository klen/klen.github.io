Простейшая реализация протокола JSONP
#####################################

:category: Blog
:date: 2011-07-05
:lang: ru
:slug: simple-jsonp
:tags: javascript, jsonp

----

.. contents:: Содержание:

----

Когда в веб-проекте необходимы кроссдоменные JSONP_ запросы, а подключать
javascript фреймворки не хочется, можно воспользоваться этой простейшей
реализацией:

.. code-block:: javascript

    // simplest JSONP request implementation
    function jsonp (url, callback) {
        var name = "jsonp" +  +new Date,
            script = document.createElement("script"),
            head = document.getElementsByTagName("head")[0];
        window[name] = callback;
        script.src = url.replace(/=\?/, "=" + name);
        head.insertBefore(script, head.firstChild);
    }


Пример использования (получение информации о пользователе с использованием API twitter.com):

.. code-block:: javascript

    var link = "http://api.twitter.com/1/statuses/user_timeline.json?screen_name=horneds&count=2&callback=?"

    jsonp(link, function (data) { alert(data) });


Пример в действии:
==================

Изменяйте значение поля ниже, на логин пользователя в твиттере, чтобы загрузить
изображение его профиля.

.. raw:: html

    <img src="#" id="img"/>
    <br/>
    <input value="horneds" onchange="get_image(this.value)" />
    <script>   
        // simplest JSONP request implementation
        function jsonp (url, callback) {
            var name = 'jsonp' +  + new Date,
                script = document.createElement('script'),
                head = document.getElementsByTagName('head')[0];
            window[name] = callback;
            script.src = url.replace(/=\?/, '=' + name);
            head.insertBefore(script, head.firstChild);
        }
        var link = "http://api.twitter.com/1/statuses/user_timeline.json?screen_name=horneds&count=2&callback=?"

        function my_callback( data ) {
            alert(data);
        }

        var image = document.getElementById('img');

        function get_image( value ) {
            var link = "http://api.twitter.com/1/statuses/user_timeline.json?screen_name=" + value + "&count=2&callback=?";
            jsonp(link, function (data) {
                image.src = data[0].user.profile_image_url;
            });
        }

        get_image( 'horneds' );
    </script>


.. _JSONP: http://en.wikipedia.org/wiki/JSONP
