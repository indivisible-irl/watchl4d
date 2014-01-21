if(!String.prototype.trim) {
    String.prototype.trim = function () {
        return this.replace(/^\s+|\s+$/g,'');
    };
}

if(!String.prototype.startswith) {
    String.prototype.startswith = function (val) {
        return this.substring(0, val.length) == val;
    };
}

if(!String.prototype.endswith) {
    String.prototype.endswith = function (val) {
        return ((this.length >= val.length) && (this.substring(this.length - val.length) == val));

    };
}

function cookie(name) {
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = $.trim(cookies[i]);
            if (cookie.startswith(name + '=')) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
    }
    return null;
}