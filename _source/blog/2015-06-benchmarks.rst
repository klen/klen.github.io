Измерение производительности популярных python web-фреймворков
==============================================================

:category: Blog
:date: 2015-06-15
:lang: ru
:slug: python-web-benchmarks
:tags: python,benchmarks,aiohttp,muffin,django,tornado,flask,falcon,pyramid,bottle

----

.. contents:: Содержание:

На праздниках решил протестировать популярные python фреймворки для web на
производительность. В отличии от других тестов не стал сосредотачиваться на
деплойменте, тестируя разнообразные связки
uwsgi/gunicorn/chaussette/waitress/nginx и тд. Но на тестировании именно самих
платформ. В частности меня интересовала «плата за асинхронность» — насколько
набирающие популярность асинхронные фреймворки превосходят/уступают синхронным
WSGI-решениям.


Участники тестирования
----------------------

.. note:: Описания взяты с оригиналов

* Aiohttp_ 0.16.3 -- Асинхронный фреймворк базирующийся на Asyncio_;
* Bottle_ 0.12.8  -- Быстрый, простой и легковесный WSGI микрофреймвок;
* Django_ 1.8.2   -- Веб-фреймворк для перфекционистов с горящими сроками;
* Falcon_ 0.3.0   -- Высоко-производительный фреймворк для построения облачных API;
* Flask_ 0.10.1   -- Микрофреймворк базирующийся на Werkzeug, Jinja2 и хороших намерениях;
* Muffin_ 0.0.88  -- Асинхронный фреймворк базирующийся на Asyncio_ и Aiohttp_;
* Pyramid_ 1.5.7  -- Небольшой, быстрый и понятный веб-фреймворк;
* Tornado_ 4.2    -- Асинхронная сетевая библиотека и веб-фреймворк;


Методика тестирования
---------------------

Тесты прогонялись на **Amazon EC2** `t2.medium <http://aws.amazon.com/ec2/instance-types/>`_ сервере.
Для создания нагрузки использовалась утилита WRK_ запущенная на том же сервере с параметрами:

::

    wrk -d30s -t12 -c400 [URL]


Все приложения (кроме Tornado) запускались при помощи Gunicorn_ (2 процесса на
каждое). Для синхронных WSGI библиотек использовался Meinheld_ worker.

Приложение на Tornado запускало 2 процесса, используя средства самого
фреймворка.

Все тесты производились с использованием **Python 3.4**.

Каждое приложение тестировалось по трем основным сценариям:

* **JSON-тест** -- закодировать небольшой объект в JSON и вернуть клиенту.

* **Remote-тест** -- требуется загрузить ответ от другого сервера и вернуть его
  клиенту.

* **Complete-тест** -- Используя ORM загрузить коллекцию объектов из базы,
  добавить к ней еще один и отрендерить список в шаблоне.

Первый сценарий это своеобразный «Hello World!» лишь несколько усложненный
процессом кодирования в JSON, что практически не влияет на результаты.
Показывает именно быстродействие в плане обработке HTTP-запросов.

Второй сценарий несколько синтетический, тк его результаты весьма предсказуемы.
Тем неменее он должен показывать насколько хорошо платформа справляется с
длительными операциями ожидания во время обработки запроса.

Третий сценарий предпалагается как комплексный тест и имитирует реальную жизнь,
а именно использование базы данных, ORM, движка шаблонов.

В качестве базы данных использовался Postgresql с дефолтными настройками.

Исходники приложений можно найти `на Github
<https://github.com/klen/py-frameworks-bench/tree/develop/frameworks>`_.


Результаты
----------

.. raw:: html

    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/jquery-bootgrid/1.2.0/jquery.bootgrid.min.css" media="screen">
    <style type="text/css" media="screen">
        .chart {
            width: 100%;
            height: 400px;
            margin: 3em 0 1.5em;
        }
        .table {
            border-collapse: collapse !important;
            font-size: .9rem;
            width: 100%;
            max-width: 100%;
            margin-bottom: 20px;
        }
        .table > thead > tr > th,
        .table > tbody > tr > th,
        .table > tfoot > tr > th,
        .table > thead > tr > td,
        .table > tbody > tr > td,
        .table > tfoot > tr > td {
            padding: 8px;
            line-height: 1.42857143;
            vertical-align: top;
            border-top: 1px solid #ddd;
        }
        .table > thead > tr > th {
            vertical-align: bottom;
            border-bottom: 2px solid #ddd;
        }
        .table > caption + thead > tr:first-child > th,
        .table > colgroup + thead > tr:first-child > th,
        .table > thead:first-child > tr:first-child > th,
        .table > caption + thead > tr:first-child > td,
        .table > colgroup + thead > tr:first-child > td,
        .table > thead:first-child > tr:first-child > td {
            border-top: 0;
        }
        .table > tbody + tbody {
            border-top: 2px solid #ddd;
        }
        .table .table {
            background-color: #fff;
        }
        .table-striped > tbody > tr:nth-of-type(odd) {
            background-color: #f9f9f9;
        }
        .table-hover > tbody > tr:hover {
            background-color: #f5f5f5;
        }
        .table > thead > tr > td.active,
        .table > tbody > tr > td.active,
        .table > tfoot > tr > td.active,
        .table > thead > tr > th.active,
        .table > tbody > tr > th.active,
        .table > tfoot > tr > th.active,
        .table > thead > tr.active > td,
        .table > tbody > tr.active > td,
        .table > tfoot > tr.active > td,
        .table > thead > tr.active > th,
        .table > tbody > tr.active > th,
        .table > tfoot > tr.active > th {
            background-color: #f5f5f5;
        }
        .table-hover > tbody > tr > td.active:hover,
        .table-hover > tbody > tr > th.active:hover,
        .table-hover > tbody > tr.active:hover > td,
        .table-hover > tbody > tr:hover > .active,
        .table-hover > tbody > tr.active:hover > th {
            background-color: #e8e8e8;
        }
        .table > thead > tr > td.danger,
        .table > tbody > tr > td.danger,
        .table > tfoot > tr > td.danger,
        .table > thead > tr > th.danger,
        .table > tbody > tr > th.danger,
        .table > tfoot > tr > th.danger,
        .table > thead > tr.danger > td,
        .table > tbody > tr.danger > td,
        .table > tfoot > tr.danger > td,
        .table > thead > tr.danger > th,
        .table > tbody > tr.danger > th,
        .table > tfoot > tr.danger > th {
            background-color: #f2dede;
        }
        .table-hover > tbody > tr > td.danger:hover,
        .table-hover > tbody > tr > th.danger:hover,
        .table-hover > tbody > tr.danger:hover > td,
        .table-hover > tbody > tr:hover > .danger,
        .table-hover > tbody > tr.danger:hover > th {
            background-color: #ebcccc;
        }
    </style>

.. raw:: html

    <div id="json" class="chart"></div>
    <table class="table table-stripped table-condensed">
        <thead>
            <tr>
                <th data-column-id="name">Name</th>
                <th data-column-id="p50" data-type="numeric">50% (ms)</th>
                <th data-column-id="p75" data-type="numeric">75% (ms)</th>
                <th data-column-id="avg" data-type="numeric">Avg (ms)</th>
                <th data-column-id="req" data-type="numeric" data-order="desc">Req/s</th>
                <th data-column-id="errors">Non 200-x</th>
                <th data-column-id="timeouts">Timeouts</th>
            </tr>
        </thead>
        <tbody>
                <tr> <td>Aiohttp</td> <td>91.67 </td> <td>103.1 </td> <td>108.01</td> <td>4093.41 </td> <td></td> <td></td> </tr>
                <tr> <td>Bottle</td>  <td>24.77 </td> <td>26.23 </td> <td>25.06 </td> <td>15761.45</td> <td></td> <td></td> </tr>
                <tr> <td>Django</td>  <td>103.2 </td> <td>112.19</td> <td>103.36</td> <td>3696.90 </td> <td></td> <td></td> </tr>
                <tr> <td>Falcon</td>  <td>19.24 </td> <td>19.81 </td> <td>19.19 </td> <td>20677.13</td> <td></td> <td></td> </tr>
                <tr> <td>Flask</td>   <td>64.32 </td> <td>71.59 </td> <td>65.68 </td> <td>6023.40 </td> <td></td> <td></td> </tr>
                <tr> <td>Muffin</td>  <td>108.07</td> <td>115.09</td> <td>171.56</td> <td>3575.36 </td> <td></td> <td></td> </tr>
                <tr> <td>Pyramid</td> <td>41.75 </td> <td>43.49 </td> <td>41.63 </td> <td>9402.69 </td> <td></td> <td></td> </tr>
                <tr> <td>Tornado</td> <td>138.24</td> <td>149.84</td> <td>136.87</td> <td>2829.72 </td> <td></td> <td></td> </tr>
        </tbody>
    </table>

В первом простом тесте с хорошим отрывом победили синхронные фреймворки. Не
считая **Django**, но в оправдание последнего, можно сказать, что по-умолчанию этот
фреймворк делает множество работы (middlewares by default). Асинхронные
фреймворки делят места аутсайдеров и неожиданно для меня на последнем месте
оказался **Tornado**. Очень хорошие результаты у **Falcon** и **Bottle**.

.. raw:: html

    <div id="remote" class="chart"></div>
    <table class="table table-stripped">
        <thead>
            <tr>
                <th data-column-id="name">Name</th>
                <th data-column-id="p50" data-type="numeric">50% (ms)</th>
                <th data-column-id="p75" data-type="numeric">75% (ms)</th>
                <th data-column-id="avg" data-type="numeric">Avg (ms)</th>
                <th data-column-id="req" data-type="numeric" data-order="desc">Req/s</th>
                <th data-column-id="errors">Non 200-x</th>
                <th data-column-id="timeouts">Timeouts</th>
            </tr>
        </thead>
        <tbody>
                <tr> <td>Aiohttp</td> <td>358.08 </td> <td>369.08  </td> <td>338.94 </td> <td>1120.27</td> <td></td> <td>     </td>  </tr>
                <tr> <td>Bottle</td>  <td>3363.74</td> <td>9911.84 </td> <td>6403.92</td> <td>19.09  </td> <td></td> <td>335  </td>  </tr>
                <tr> <td>Django</td>  <td>3317.64</td> <td>12954.23</td> <td>6918.64</td> <td>18.96  </td> <td></td> <td>300  </td>  </tr>
                <tr> <td>Falcon</td>  <td>3196.23</td> <td>12976.84</td> <td>6696.17</td> <td>19.28  </td> <td></td> <td>328  </td>  </tr>
                <tr> <td>Flask</td>   <td>3306.88</td> <td>11690.8 </td> <td>6824.88</td> <td>19.16  </td> <td></td> <td>363  </td>  </tr>
                <tr> <td>Muffin</td>  <td>372.95 </td> <td>428.75  </td> <td>376.98 </td> <td>1019.76</td> <td></td> <td>     </td>  </tr>
                <tr> <td>Pyramid</td> <td>3295.1 </td> <td>10518.92</td> <td>6673.78</td> <td>19.35  </td> <td></td> <td>338  </td>  </tr>
                <tr> <td>Tornado</td> <td>1994.39</td> <td>2069.25 </td> <td>1928.31</td> <td>194.37 </td> <td></td> <td>     </td> </tr>
        </tbody>
    </table>

Для понимания результатов следующего теста необходимо пояснить, что приложения
обращались к nginx настроенному на ответ с задержкой 100ms. Из-за этого
результаты синхронных фреймворков очень близки, практически вся их работа после
определенного момента сводилась к ожиданию. Опять неожиданные результаты от
**Tornado**, я предполагал, что он будет близок к **Aiohttp** и **Muffin**. Но тем неменее 
**Tornado** в 10 раз эффективнее в этом кейсе чем ближайший синхронный фреймворк.

.. raw:: html

    <div id="complete" class="chart"></div>
    <table class="table table-stripped">
        <thead>
            <tr>
                <th data-column-id="name">Name</th>
                <th data-column-id="p50" data-type="numeric">50% (ms)</th>
                <th data-column-id="p75" data-type="numeric">75% (ms)</th>
                <th data-column-id="avg" data-type="numeric">Avg (ms)</th>
                <th data-column-id="req" data-type="numeric" data-order="desc">Req/s</th>
                <th data-column-id="errors">Non 2xx</th>
                <th data-column-id="timeouts">Timeouts</th>
            </tr>
        </thead>
        <tbody>
                <tr> <td>Aiohttp</td> <td>151.78 </td> <td>156.9  </td> <td>254.75 </td> <td>1004.82</td> <td>68%</td> <td>236  </td> </tr>
                <tr> <td>Bottle</td>  <td>613.5  </td> <td>630.17 </td> <td>1062.86</td> <td>451.34 </td> <td></td>    <td>178  </td> </tr>
                <tr> <td>Django</td>  <td>1610.46</td> <td>1976.44</td> <td>2632.36</td> <td>88.57  </td> <td></td>    <td>42   </td> </tr>
                <tr> <td>Falcon</td>  <td>766.75 </td> <td>805.35 </td> <td>1457.99</td> <td>350.26 </td> <td></td>    <td>81   </td> </tr>
                <tr> <td>Flask</td>   <td>1032.63</td> <td>1649.89</td> <td>1465.25</td> <td>222.78 </td> <td></td>    <td>496  </td> </tr>
                <tr> <td>Muffin</td>  <td>420.14 </td> <td>485.4  </td> <td>1552.7 </td> <td>819.62 </td> <td></td>    <td>     </td> </tr>
                <tr> <td>Pyramid</td> <td>562.44 </td> <td>601.49 </td> <td>812.43 </td> <td>248.42 </td> <td></td>    <td>235  </td> </tr>
                <tr> <td>Tornado</td> <td>937.37 </td> <td>988.86 </td> <td>910.06 </td> <td>418.36 </td> <td></td>    <td>     </td> </tr>
        </tbody>
    </table>

И последний тест. Результаты Aiohttp можно игнорировать тк к сожалению более двух третей запросов вернули 502 ошибки.
На первом месте неожиданно, но приятно, оказался мой фреймворк Muffin_ достаточно быстро обрабатывающий этот тест.
Django_ значительно проигрывает, лишь подтверждая медлительность стандартного движка шаблонов и ORM.

.. raw:: html

    <script language="javascript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
    <script language="javascript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/highcharts/4.1.5/highcharts.js"></script>
    <script language="javascript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery-bootgrid/1.2.0/jquery.bootgrid.min.js"></script>
    <script language="javascript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery-bootgrid/1.2.0/jquery.bootgrid.fa.min.js"></script>
    <script language="javascript" type="text/javascript">
        (function($){
            $(function () { 

                var data = {
                    "pyramid": [[0.26, 41.75, 43.49, 45.49, 48.83, 204.31, 412.87, 41.63, 30.04, 282457.0, 0.0, 0.0, 0.0], [123.16, 3295.1, 10518.92, 17411.24, 23569.44, 24190.6, 24190.6, 6673.78, 30.07, 582.0, 0.0, 338.0, 0.0], [44.73, 562.44, 601.49, 872.25, 9289.18, 14654.82, 14714.02, 812.43, 30.09, 7475.0, 0.0, 235.0, 0.0]], 
                    "aiohttp": [[1.96, 91.67, 103.1, 107.48, 848.42, 1892.42, 2347.08, 108.01, 30.05, 123007.0, 0.0, 0.0, 0.0], [104.16, 358.08, 369.08, 380.07, 402.21, 703.7, 904.4, 338.94, 30.04, 33653.0, 0.0, 0.0, 0.0], [2.58, 151.78, 156.9, 161.79, 5906.94, 12441.32, 13993.53, 254.75, 30.05, 30195.0, 20442.0, 236.0, 0.0]], 
                    "flask": [[1.13, 64.32, 71.59, 74.38, 78.11, 328.78, 551.97, 65.68, 30.04, 180943.0, 0.0, 0.0, 0.0], [118.92, 3306.88, 11690.8, 16981.66, 22278.62, 29043.58, 29043.58, 6824.88, 30.06, 576.0, 0.0, 363.0, 0.0], [35.75, 1032.63, 1649.89, 2726.3, 8822.6, 10403.23, 10478.41, 1465.25, 30.07, 6699.0, 0.0, 496.0, 0.0]], 
                    "muffin": [[2.41, 108.07, 115.09, 120.97, 2554.97, 4252.73, 4996.43, 171.56, 30.04, 107404.0, 0.0, 0.0, 0.0], [108.61, 372.95, 428.75, 449.83, 487.94, 1300.74, 1564.79, 376.98, 30.05, 30644.0, 0.0, 0.0, 0.0], [9.17, 420.14, 485.4, 4964.92, 16890.25, 21367.9, 23015.05, 1552.7, 30.06, 24638.0, 0.0, 0.0, 0.0]], 
                    "django": [[5.75, 103.2, 112.19, 114.23, 117.67, 445.56, 681.68, 103.36, 30.04, 111055.0, 0.0, 0.0, 0.0], [121.64, 3317.64, 12954.23, 18790.94, 21321.65, 27579.58, 27579.58, 6918.64, 30.06, 570.0, 0.0, 300.0, 0.0], [155.24, 1610.46, 1976.44, 6974.99, 14514.59, 20437.6, 20478.44, 2632.36, 30.1, 2666.0, 0.0, 42.0, 0.0]], 
                    "tornado": [[1.61, 138.24, 149.84, 156.4, 161.76, 169.15, 311.63, 136.87, 30.04, 85005.0, 0.0, 0.0, 0.0], [178.48, 1994.39, 2069.25, 2087.02, 2126.76, 2239.36, 2300.74, 1928.31, 30.05, 5841.0, 0.0, 0.0, 0.0], [19.12, 937.37, 988.86, 1015.01, 1049.07, 1576.72, 1603.96, 910.06, 30.06, 12576.0, 0.0, 0.0, 0.0]], 
                    "bottle": [[0.19, 24.77, 26.23, 27.45, 31.91, 103.28, 295.81, 25.06, 30.04, 473474.0, 0.0, 0.0, 0.0], [122.9, 3363.74, 9911.84, 16793.91, 22170.11, 25412.56, 25412.56, 6403.92, 30.06, 574.0, 0.0, 335.0, 0.0], [37.44, 613.5, 630.17, 1866.8, 8491.27, 12824.83, 14535.27, 1062.86, 30.05, 13563.0, 0.0, 178.0, 0.0]], 
                    "falcon": [[0.13, 19.24, 19.81, 20.45, 22.3, 100.12, 273.87, 19.19, 30.09, 622175.0, 0.0, 0.0, 0.0], [123.16, 3196.23, 12976.84, 16166.13, 21823.98, 24082.81, 24082.81, 6696.17, 30.07, 580.0, 0.0, 328.0, 0.0], [26.47, 766.75, 805.35, 3142.8, 14607.38, 17632.72, 17883.95, 1457.99, 30.1, 10543.0, 0.0, 81.0, 0.0]]
                };

                var frameworks = [
                    'aiohttp',
                    'bottle',
                    'django',
                    'falcon',
                    'flask',
                    'muffin',
                    'pyramid',
                    'tornado',
                ],
                    categories = ["min", "50%", "75%", "90%", "99.9%", "max"],
                    series = [],
                    common_options = {
                        xAxis: {
                            categories: categories,
                            startOnTick: true
                        },
                        yAxis: {
                            title: { text: 'Values (ms)' },
                            min: 0
                        },
                        tooltip: {
                            valueSuffix: 'ms'
                        },
                        legend: {
                            layout: 'vertical',
                            align: 'right',
                            verticalAlign: 'middle',
                            borderWidth: 0
                        },
                        chart: {
                            zoomType: 'y',
                            type: 'spline'
                        }
                    };

                for (i in [0, 1, 2]) {
                    var cur = series[i] = [], pie = {
                        name: 'mid', type: 'pie', dataLabels: { enabled: true, format: '{point.name} {point.y:.2f} ms'},
                        data: [], center: [100, 80], size: 100};

                    for (n in data) {
                        if (data[n][i] instanceof Array) {
                            pie.data.push({name: n, y: data[n][i][2]})
                            cur.push({
                                name: n,
                                data: data[n][i].slice(0, 4)
                            });
                        }
                    };
                    cur.push(pie);
                };

                $('#json').highcharts($.extend({
                    title: { text: 'Encode a object to JSON and return as response' },
                    subtitle: { text: 'lower is better' },
                    series: series[0]}, common_options));

                $('#remote').highcharts($.extend({
                    title: { text: 'Load a response from remote server and return as response' },
                    subtitle: { text: 'lower is better' },
                    series: series[1]}, common_options));

                $('#complete').highcharts($.extend({
                    title: { text: 'Load data from database with ORM and render to template' },
                    subtitle: { text: 'lower is better' },
                    series: series[2]}, common_options));

                $('table').bootgrid({ navigation: 0 });

            });
        
        })(jQuery);
    </script>


Выводы
------

Я предлагаю читателю сделать их самостоятельно. Данное тестирование
производилось мой чтобы понять выгоду использования синхронных/асинхронных
библиотек и показатели производительности популярных решений.

В дальнейшем планирую проводить данные измерения регулярно.



.. _Asyncio:  https://www.python.org/dev/peps/pep-3156/
.. _Aiohttp:  https://github.com/KeepSafe/aiohttp
.. _Bottle:   https://github.com/bottlepy/bottle
.. _Django:   https://github.com/django/django
.. _Falcon:   https://github.com/falconry/falcon
.. _Flask:    https://github.com/mitsuhiko/flask
.. _Muffin:   https://github.com/klen/muffin
.. _Pyramid:  https://github.com/Pylons/pyramid
.. _Tornado:  https://github.com/tornadoweb/tornado
.. _Gunicorn: http://gunicorn.org/
.. _Meinheld: http://meinheld.org/
.. _WRK:  https://github.com/wg/wrk
