Site.Controls.Slide = Backbone.View.extend({
    width: null,

    initialize: function (options) {
        options = options || {};
        this.width = options.width || this.width;

        this.$el.css({
            width: '100%',
            height: '100%',
            position: 'absolute',
            left: '0px',
            top: '0px'
        });
        this.$el.parent().css({
            overflow: 'hidden',
            position: 'relative',
            top: '0px',
            left: '0px'
        });
    },

    getParentWidth: function () {
        return this.width ? this.width : this.$el.parent().width();
    },

    getWidthPixels: function (percentage) {
        return this.getParentWidth() * (percentage / 100);
    },

    setLeft: function () {
        this.$el.css('x', this.getWidthPixels(-15));
        return this;
    },

    setCenter: function () {
        this.$el.css('x', 0);
        return this;
    },

    setRight: function () {
        this.$el.css('x', this.getWidthPixels(105));
        return this;
    },

    slideCenter: function (callback) {
        this.$el.transition({x: 0}, callback);
        return this;
    },

    slideLeft: function (callback) {
        this.$el.transition({x: this.getWidthPixels(-15)}, callback);
        return this;
    },

    slideRight: function (callback) {
        this.$el.transition({x: this.getWidthPixels(105)}, callback);
        return this;
    },

    remove: function () {
        this.$el.remove();
    }
});

Site.Controls.Slider = Backbone.View.extend({
    slides: null,
    current: null,

    initialize: function (options) {
        options = options || {};
        var width = options.width || null;
        var elements = options.elements || [];

        this.slides = [];
        _.each(elements, function (element) {
            var slide = new Site.Controls.Slide({
                el: element,
                width: width
            });
            this.slides.push(slide);
        }, this);

        this.set(0);
    },

    set: function (index) {
        _.each(this.slides, function (slide, i) {
            if (i < index) {
                slide.setLeft();
            }
            else if (i == index) {
                slide.setCenter();
            }
            else {
                slide.setRight();
            }
        }, this);

        this.current = index;
    },

    slide: function (index, callback) {
        if (this.current == index) {
            if (callback) {
                callback();
            }
            return;
        }

        _.each(this.slides, function (slide, i) {
            if (this.current < index) {
                if (i == index) {
                    slide.$el.css('z-index', 2);
                }
                else if (i == this.current) {
                    slide.$el.css('z-index', 1);
                }
                else {
                    slide.$el.css('z-index', 0);
                }
            }
            else {
                if (i == index) {
                    slide.$el.css('z-index', 1);
                }
                else if (i == this.current) {
                    slide.$el.css('z-index', 2);
                }
                else {
                    slide.$el.css('z-index', 0);
                }
            }
        }, this);

        if (this.current < index) {
            // We are shifting everything left
            this.slides[this.current].setCenter().slideLeft();
            this.slides[index].setRight().slideCenter(callback);

        }
        else {
            // We are shifting everything right
            this.slides[this.current].setCenter().slideRight();
            this.slides[index].setLeft().slideCenter(callback);
        }

        this.current = index;
    },

    add: function (element, callback) {
        if (!element.parent().exists()) {
            this.$el.append(element);
        }
        var slide = new Site.Controls.Slide({el: element});
        this.slides.push(slide);

        var callback_and_remove = $.proxy(function () {
            callback();
            this.removeHidden();
        }, this);
        this.slide(this.slides.length - 1, callback_and_remove);
    },

    removeHidden: function () {
        var currentSlide = this.slides[this.current];

        _.each(this.slides, function (slide, i) {
            if (this.current != i) {
                slide.remove();
            }
        }, this);

        this.slides = [currentSlide];
        this.current = 0;
    }

});