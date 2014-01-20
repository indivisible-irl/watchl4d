Site.Views.AuthPanel = Backbone.View.extend({

    events: {
        'click #login': 'onClickLogin',
        'click #register': 'onClickRegister',
        'click #logout': 'onClickLogout',
        'click #yourteam': 'onClickYourTeam'
    },

    render: function () {
        this.$el.html(JST.auth_panel({model: Site.User}));
        return this;
    },

    onClickLogin: function (e) {
        new Site.Views.LoginDialog;
    },

    onClickRegister: function (e) {
        new Site.Views.RegisterDialog;
    },

    onClickLogout: function (e) {
        $.ajax({url: Settings.ROOT_URL + '/logout/', type: 'GET'});
        Site.User.clear();
        return false;
    },

    onClickYourTeam: function (e) {
        new Site.Views.YourTeamDialog;
    }

});