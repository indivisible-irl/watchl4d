Site.Models.Base = Backbone.Model.extend({
    parse: function (response, options) {
        if (this.collection)
            return response;
        return response.data;
    }
});

Site.Models.User = Site.Models.Base.extend({
    // images: null,
    // tracks: null,
    set: function (attributes, options) {
        // var attributes = attributes || {},
        //     images = attributes.images || [],
        //     tracks = attributes.tracks || [];
        // if (!this.images) {
        //     this.images = new Site.Collections.Images(images);
        // }
        // else {
        //     this.images.set(images);
        // }
        // if (!this.tracks) {
        //     this.tracks = new Site.Collections.Tracks(tracks);
        // }
        // else {
        //     this.tracks.set(tracks);
        // }

        // parent is called last to ensure events are triggered after
        // everything is set
        Site.Models.Base.prototype.set.call(this, attributes, options);
    },

    // isBand: function () {
    //     return (!this.isNew()) && (this.get('type') == Site.Constants.TYPE_BAND);
    // }
});