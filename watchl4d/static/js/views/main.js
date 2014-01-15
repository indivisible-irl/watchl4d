Site.Views.Main = Backbone.View.extend({
    el: 'body',

    // player: null,

    // authPanel: null,
    // trackPanel: null,
    // friendPanel: null,

    // events: {
    //     'click .side-button-upload': 'onClickUpload',
    //     'click .side-button-friends': 'onClickFriends',
    //     'click .side-button-music': 'onClickMusic'
    // },

    // initialize: function (options) {
    //     this.authPanel = new Site.Views.AuthPanel({el: this.$('.auth-panel')});

    //     this.player = new Site.Views.Player;
    //     this.$('.player').append(this.player.render().el);
        
    //     this.trackPanel = new Site.Views.TrackSidePanel;
    //     this.friendPanel = new Site.Views.FriendSidePanel;

    //     this.listenTo(Site.User, 'change', this.onUserChange);
    // },

    // render: function () {
    //     this.authPanel.render();

    //     var sideButtonUpload = this.$('.side-button-upload'),
    //         sideButtonFriends = this.$('.side-button-friends'),
    //         sideButtonMusic = this.$('.side-button-music');

    //     sideButtonFriends.transition({opacity: 100});

    //     if (Site.User.isBand()) {
    //         sideButtonUpload.css({display: ''}).transition({top: '56px', opacity: 100});
    //         sideButtonMusic.css({display: ''}).transition({top: '97px', opacity: 100});
    //     }
    //     else {
    //         sideButtonUpload.transition({top: '0px', opacity: 0}).promise().done(function () {
    //             sideButtonUpload.css({display: 'none'});
    //         });
    //         sideButtonMusic.transition({top: '0px', opacity: 0}).promise().done(function () {
    //             sideButtonMusic.css({display: 'none'});
    //         });
    //     }
    //     return this;
    // },

    // onUserChange: function () {
    //     this.render();
    // },

    // onClickUpload: function (e) {
    //     new Site.Views.UploadDialog;
    // },

    // onClickFriends: function (e) {
    //     this.friendPanel.open();
    // },

    // onClickMusic: function (e) {
    //     this.trackPanel.open();
    // }

});
