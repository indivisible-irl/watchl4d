Site.Views.Dialog = Backbone.View.extend({
    className: 'dialog',

    title: 'Title',
    html: 'Content',

    events: {
        'click': 'onClick',
        'click .dialog-inner': 'onClickInner',
        'click .icon-x': 'onClickCancel',
        'submit form': 'onSubmit',
        'click a': 'onClickLink'
    },

    initialize: function (options) {
        options = options || {};
        this.title = options.title || this.title;
        this.html = options.html || this.html;
        this.render();
    },

    render: function () {
        this.$el.html(window.JST.dialog({
            title: this.title, 
            html: this.html
        }));
        this.open();
        return this;
    },

    open: function () {
        $('body').append(this.$el);
        _.defer(function (self) {
            self.$('.dialog-inner').transition({
                scale: 1, 
                easing: 'easeOutBack', 
                duration: 200
            });
        }, this);
    },

    close: function () {
        var self = this;
        this.$('.dialog-inner').transition({
            scale: 0,
            easing: 'easeInBack',
            duration: 200
        }).promise().done(function () {
            self.remove();  // have to do this instead of "complete" callback because bug in transit.
        });
    },

    onClick: function (e) {
        this.close();
    },

    onClickInner: function (e) {
        e.stopPropagation();
    },

    onClickCancel: function (e) {
        this.close();
    },

    onSubmit: function (e) {
        return false;
    },

    onClickLink: function (e) {
        return false;
    },

    showSpinner: function () {
        this.$('.spinner').slideDown(200);
    },

    hideSpinner: function () {
        this.$('.spinner').slideUp(200);
    },

    showError: function (html) {
        this.$('.error').html(html).slideDown(200);
    },

    hideError: function (html) {
        this.$('.error').slideUp(200);
    },
});

Site.Views.LoginDialog = Site.Views.Dialog.extend({
    title: 'Login',
    render: function () {
        
        this.$el.html(window.JST.dialog({
            title: this.title,
            html: window.JST.login()
        }));

        this.open();
        return this;
    },

    onClickLink: function (e) {
        this.close();
        new Site.Views.RegisterDialog;
    },

    onSubmit: function (e) {
        var username = this.$('#username'),
            password = this.$('#password');
        
        this.hideError();
        this.hideSpinner();

        var msg = username.assertRequired('Username');
        msg += password.assertRequired('Password');
        
        if (msg) {
            this.showError(msg)
            return false;
        }
        
        this.showSpinner();
        
        $.ajax({
             url: Settings.ROOT_URL + '/login/',
             context: this,
             type: 'POST',
             dataType: 'json',
             data: {'username': username.val(),
                    'password': password.val()},
             headers: {'X-CSRFToken': cookie('csrftoken')},
             success: function (data, textStatus, jqXHR) {
                 if (!data.success) {
                    this.showError(data.message);
                 }
                 else {
                     Site.User.set(data.data);
                     this.close();
                 }
             },
             error: function (jqXHR, textStatus, errorThrown) {
                this.showError('Something went wrong. Please try again.');
             },
             complete: function (jqXHR, textStatus) {
                this.hideSpinner();
             }
        });
        return false;
    }
});

Site.Views.RegisterDialog = Site.Views.Dialog.extend({
    title: 'Sign Up',

    render: function () {
        
        this.$el.html(window.JST.dialog({
            title: this.title,
            html: window.JST.register()
        }));

        this.open();
        return this;
    },

    onClickLink: function (e) {
        this.close();
        new Site.Views.LoginDialog;
    },

    onSubmit: function (e) {
        var name = this.$('#name'),
            steam_id = this.$('#steam_id'),
            steam_profile = this.$('#steam_profile'),
            username = this.$('#username'),
            password = this.$('#password'),
            confirm = this.$('#confirm_password'),

        this.hideError();
        this.hideSpinner();

        var msg += name.assertRequired('Name');
        msg += steam_id.assertRequiredSyntaxSteamId();
        msg += username.assertRequired('Username');
        msg += password.assertRequired('Password');
        msg += password.assertEqual('Password', confirmpassword, 'Confirmation Password');

        if (msg) {
            this.showError(msg);
            return false;
        }
        
        this.showSpinner();
        
        $.ajax({
            url: Settings.ROOT_URL + '/register/',
            context: this,
            type: 'POST',
            dataType: 'json',
            data: {'name': name.val(),
                    'steam_id': steam_id.val(),
                    'steam_profile': steam_profile.val(),
                    'username': username.val(),
                    'password': password.val()},
            headers: {'X-CSRFToken': cookie('csrftoken')},
            success : function (data, textStatus, jqXHR) {
                if (!data.success) {
                    this.showError(data.message);
                }
                else {
                    Site.User.set(data.data);
                    this.close();
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                this.showError('Something went wrong.  Please try again.');
            },
            complete: function (jqXHR, textStatus) {
                this.hideSpinner();
            }
        });
        return false;
    }
});

Site.Views.YourTeamDialog = Site.Views.Dialog.extend({
    title: 'Your Team',

    events: {
        'submit #edit_team': 'onSubmitEditTeam',
        'submit #delete_team': 'onSubmitDeleteTeam',
        'click #cancel': 'onClickCancel'
    },

    render: function () {
        
        this.$el.html(window.JST.dialog({
            title: this.title,
            html: window.JST.yourteam({model: Site.User})
        }));

        this.open();
        return this;
    },

    validateTeam: function () {
        var teamName = this.$('#team_name').val();

        var msg = teamName.assertRequired('Team Name')
        for (var i = 0; i < 6; i++)
            msg += this.validateMember(i);
    
        this.showError(msg);
        return msg == '';
    },

    validateMember: function (index) {
        var playerName = this.$('#name' + index).val();
        var playerSteamId = $('#steam_id' + index).val();
    
        if (index == 0)
        {
            var msg = playerName.assertRequired('Player 1\'s name (you)');
            msg += playerSteamId.assertRequiredSyntaxSteamId('Player 1\'s Steam ID (yours)');
        }
        else
        {
            var msg = '';
            if (playerName.trim() != '')
                msg += playerSteamId.assertRequiredSyntaxSteamId('Player ' + (index + 1) + '\'s Steam ID');
        }
    
        return msg;
    },

    onClickCancel: function (e) {
        this.close();
    },

    onSubmitEditTeam: function (e) {
        if (!this.validateTeam()) {
            return false;
        }

        this.showSpinner();
        
        var data = {};
        data['team_name'] = this.$('#team_name').val();
        data['team_active'] = this.$('#team_active').prop('checked');
        for (var i = 0; i < 8; i++) {
            data['id' + i] = this.$('#id' + i).val();
            data['name' + i] = this.$('#name' + i).val();
            data['steam_id' + i] = this.$('#steam_id' + i).val();
            data['steam_profile' + i] = this.$('#steam_profile' + i).val();
        }

        // this.locked = true;
        // var view = this;
        $.ajax({
             url: Settings.ROOT_URL + '/team/',
             type: 'POST',
             dataType: 'json',
             data: data,
             context: this,
             headers: {'X-CSRFToken': cookie('csrftoken')},
             success : function (data, textStatus, jqXHR) {
                this.showError(data.message);
                view.$('.error').html(data.message);
                if (data.success) {
                    Site.User.set(data.data);
                }
             },
             error: function (jqXHR, textStatus, errorThrown) {
                this.showError('Something went wrong. Please try again.');
             },
             complete: function (jqXHR, textStatus) {
                // view.locked = false;   
                this.hideSpinner();
             }
         });
         return false;
    },

    onSubmitDeleteTeam: function (e) {
        if (!confirm('Are you sure you want to delete your team?')) {
            return false;
        }

        $.ajax({
             url: Settings.ROOT_URL + '/deleteteam/',
             type: 'POST',
             dataType: 'json',
             data: data,
             context: this,
             headers: {'X-CSRFToken': cookie('csrftoken')},
             success : function (data, textStatus, jqXHR) {
                this.showError(data.message);
                if (data.success) {
                    Site.User.set(data.data);
                }
             },
             error: function (jqXHR, textStatus, errorThrown) {
                 this.showError('Something went wrong. Please try again.');
             },
             complete: function (jqXHR, textStatus) {
                this.hideSpinner();
             }
         });

        return false;
    }

});

