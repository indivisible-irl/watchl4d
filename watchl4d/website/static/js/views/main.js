Site.Views.Main = Backbone.View.extend({
    el: 'body',

    authPanel: null,
    slider: null,

    initialize: function (options) {
        this.authPanel = new Site.Views.AuthPanel({el: this.$('.auth-panel')});

        this.$('#home-panel').html(JST.home);
        this.$('#teams-panel').html(JST.teams);
        this.$('#rules-panel').html(JST.rules);
        this.$('#resources-panel').html(JST.resources);

        this.slider = new Site.Controls.Slider({
            elements: [
                this.$('#home-panel'),
                this.$('#teams-panel'),
                this.$('#rules-panel'),
                this.$('#resources-panel'),
            ]
        });
    },

    render: function () {
        this.authPanel.render();
        return this;
    },

    onUserChange: function () {
        this.render();
    }

});
