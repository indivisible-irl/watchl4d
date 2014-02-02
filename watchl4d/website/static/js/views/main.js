Site.Views.Main = Backbone.View.extend({
    el: 'body',

    authPanel: null,
    slider: null,

    roundsLoaded: [],

    events: {
        'submit .post': 'onSubmitPost'
    },

    initialize: function (options) {
        this.authPanel = new Site.Views.AuthPanel({el: this.$('.auth-panel')});

        this.$('#home-panel').html(JST.home);
        this.$('#rules-panel').html(JST.rules);
        this.$('#resources-panel').html(JST.resources);

        this.$('.slide').each(function (i, slide) {
            var number = $(slide).attr('data-number');
            if (number) {
                $(slide).html(JST.round_unloaded({number: number}));
            }
        });

        this.slider = new Site.Controls.Slider({
            elements: this.$('.slide')
        });

        this.listenTo(Site.User, 'change', this.onUserChange);
    },

    render: function () {
        this.authPanel.render();
        return this;
    },

    onUserChange: function () {
        this.render();
    },

    onRoundSlide: function () {
        var number = Site.Main.slider.current - 3;
        if (Site.Main.roundsLoaded.indexOf(number) != -1) {
            // We've already loaded this round; no-op
            return;
        }

        $.ajax({
            url: Settings.ROOT_URL + 'round/' + number + '/', 
            type: 'GET',
            dataType: 'json',
            success: function (data, textStatus, jqXHR) {
                if (!data.success) {
                    return;
                }

                Site.Main.$('.slide').each(function (i, slide) {
                    var slideNumber = $(slide).attr('data-number');
                    if (!slideNumber || (Number(slideNumber) != number)) {
                        return;
                    }

                    $(slide).html(JST.round({model: new Backbone.Model(data.data)}));
                });
            },
            error: function (jqXHR, textStatus, errorThrown) {
            },
            complete: function (jqXHR, textStatus) {
            }
        });
    },

    onSubmitPost: function (e) {
        var form = event.target,
            text = $(form).find('#text'),
            error = $(form).find('.error'),
            spinner = $(form).find('.spinner'),
            progress = $(form).find('.progress'),
            bar = $(form).find('.bar'),
            filename = $(form).find('#file').filename();

        progress.slideUp();
        spinner.slideUp();
        bar.css('width', '0%');
        error.slideUp();

        var msg = text.assertRequired('Text');

        if (filename && !FormData) {
            msg += 'File uploads on your browser are not supported. <br />';
        }
        
        if (msg) {
            error.html(msg).slideDown();
            return false;
        }

        if (filename) {
            progress.slideDown();
        }
        else {
            spinner.slideDown();
        }
        
        view = this;
         $.ajax({
             url: Settings.ROOT_URL + '/post/',
             type: 'POST',
             dataType: 'json',
             data: new FormData(form),
             cache: false,
             contentType: false,
             processData: false,
             xhr: function () {
                 x = $.ajaxSettings.xhr();
                 if (x.upload && filename) {
                     x.upload.addEventListener('progress',
                        function (e) {
                            var p = (e.loaded / e.total) * 100;
                            bar.css('width', p + '%');
                        }, false);
                     x.upload.addEventListener('load',
                        function (e) {
                            bar.css('width', '100%');
                        }, false);
                 }
                 return x;
             },
             headers: {'X-CSRFToken': cookie('csrftoken')},
             success : function (data, textStatus, jqXHR) {
                 if (!data.success) {
                     error.html(data.message).slideDown();
                 }
                 else {
                     error.html(data.message).slideDown();
                     location.reload();
                 }
             },
             error: function (jqXHR, textStatus, errorThrown) {
                 error.html('Something went wrong. Please try again.').slideDown();
             },
             complete: function (jqXHR, textStatus) {
                spinner.slideUp();
             }
         });
         return false;
    }

});
