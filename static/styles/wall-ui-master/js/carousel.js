
(function ($) {
    $.fn.extend({
        carousel: function (options) {

            var defaults = {
                'carouselItem': '.item',
                'duration': 800,
				'itemWidth' : 320,
                'next': '.next',
                'prev': '.prev'
            };

            var options = $.extend(defaults, options);

            return this.each(function () {
                var carousel = $(this);

                var o = options;

                var carouselItem = o.carouselItem;
                var duration = o.duration;
				var itemWidth = o.itemWidth;
                var easing = o.easing;
                var next = o.next;
                var prev = o.prev;

                var clonedCarouselItems = $(carouselItem).clone();
                carousel.append(clonedCarouselItems);
				
                var leftValue = itemWidth * (-1);

                $(carouselItem).first().before($(carouselItem).last());
                carousel.css({ 'left': leftValue });


                function gotoNext() {
                    var leftIndent = parseInt(carousel.css('left')) - itemWidth;
                    carousel.not(':animated').animate({ 'left': leftIndent }, duration, function () {
                        $(carouselItem).last().after($(carouselItem).first());
                         carousel.css({ 'left': leftValue });
                    });
                }
				
				setInterval(gotoNext, 3000);
            });
        }
    });
})(jQuery);
