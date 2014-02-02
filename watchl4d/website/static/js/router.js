Site.Routers.Main = Backbone.Router.extend({
    routes: {
        'home': 'home',
        'teams': 'teams',
        'rules': 'rules',
        'resources': 'resources',
        'round/:number': 'round'
    },
    home: function () {
        Site.Main.slider.slide(0);
    },
    teams: function () {
        Site.Main.slider.slide(1);
    },
    rules: function () {
        Site.Main.slider.slide(2);
    },
    resources: function () {
        Site.Main.slider.slide(3);
    },
    round: function (number) {
        Site.Main.slider.slide(Number(number) + 3, Site.Main.onRoundSlide);
    }
});