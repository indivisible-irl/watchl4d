Site = {
    Events: {},
    Views: {},
    Models: {},
    Collections: {},
    Routers: {},
    Controls: {},
    Tools: {},
    
    Constants: {
        TYPE_LISTENER: 0,
        TYPE_BAND: 1
    },

    Router: null,
    Main: null,
    User: null
};

_.extend(Site.Events, Backbone.Events);

$(function () {
    Site.User = new Site.Models.User(Session.user);
    Site.Main = new Site.Views.Main;
    Site.Router = new Site.Routers.Main;
    Backbone.history.start();
    Site.Main.render();
});