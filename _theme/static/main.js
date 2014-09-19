require('zeta://zeta.js');
require('blocks/escapes.min.js');

String.prototype.format = function (data) {
    var s = this;
    for (var k in data) {
        s = s.replace(new RegExp('{' + k + '}', 'g'), data[k]);
    }
    return s;
};

zeta.blocks.twitter = function( params ){
    var self = this;
    $.getJSON("http://api.twitter.com/1/statuses/user_timeline.json?screen_name=horneds&count=2&callback=?",
        function (tweets) {
            var date = new Date(tweets[0].created_at);
            var data = {id: tweets[0].id, text: tweets[0].text};
            var tmpl = '<a href="http://twitter.com/#!/horneds/">{text}</a>';
            self.html(tmpl.format(data));
    });
};

zeta.blocks.article_paginator = function( params ){
    var self = this;
    var left = self.find('.article_paginator_left_link'),
        right = self.find('.article_paginator_right_link');

    $(document).keydown( function(e){
        if (e.ctrlKey && e.keyCode == 39 && right.length){
            document.location.href = right.attr('href');
        };
        if (e.ctrlKey && e.keyCode == 37 && left.length){
            document.location.href = left.attr('href');
        };
    } );
};

zeta.blocks.ans = function (params) {
    var self = this;
    escapes('theme/ansi/' + Math.ceil(Math.random() * 10) + '.ans', function(){
        $(this).appendTo(self);
    });
};

zeta.blocks.cloud = function(params) {
    var self = this, offset = 0;
    $(document).bind("mousemove keyup keydown", function(e){
        offset += 1;
        self.css("backgroundPosition", offset + "px 0");
    });
};
