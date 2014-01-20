
$.fn.exists = function () {
    return this.length > 0;
}

/*
 * Cousin to fadeOut except doesn't set display = none
 * and disables any custom cursor that may give away the elements position
 */
$.fn.blurOut = function (duration, destOpacity) {
    duration = duration || 0;
    
    var origCursor = this.css('cursor'),
        origOpacity = Number(this.css('opacity')),
        destOpacity = _.isUndefined(destOpacity) ? 0.3 : destOpacity,
        opacity = origOpacity < destOpacity ? origOpacity : destOpacity;
    
    this.data('blurOut:origCursor', origCursor);

    this.animate({opacity: opacity}, duration, 'swing',
        function () {
            $(this).css({cursor: 'default'});
        });
    return this;
};

/*
 * Cousin to fadeIn but only effects opacity and will reset
 * the element's cursor to what it was prior to calling blurOut (if applicable)
 */
$.fn.blurIn = function (duration) {
    duration = duration || 0;
    
    var origCursor = this.data('blurOut:origCursor'),
        cursor = origCursor || 'auto';

    this.css({cursor: cursor});
    this.animate({opacity: 1}, duration);
    return this;
};

 $.fn.isVisible = function () {
    return this.css('visibility') == 'visible';
 }

 $.fn.visible = function () {
    return this.css({'visibility': 'visible'});
 }

 $.fn.hidden = function () {
    return this.css({'visibility': 'hidden'});
 }

 $.fn.animationPlayStateIsRunning = function () {
    return this.css('-webkit-animation-play-state') == 'running';
}

$.fn.animationPlayStateRunning = function () {
    this.css('-webkit-animation-play-state', 'running');
    this.css('-moz-animation-play-state', 'running');
    return this;
}

$.fn.animationPlayStatePaused = function () {
    this.css('-webkit-animation-play-state', 'paused');
    this.css('-moz-animation-play-state', 'paused');
    return this;
}

$.fn.animationName = function (name) {
    this.css('-webkit-animation-name', name);
    this.css('-moz-animation-name', name);
    return this;
}

$.fn.animationDuration = function (duration) {
    this.css('-webkit-animation-duration', duration);
    this.css('-moz-animation-duration', duration);
    return this;
}

/*
 * Intended to be used on a file input element
 * to retrieve the filename with any path info stripped from it.
 */
$.fn.filename = function () {
    return _.last(this.val().split('\\'));
}

/******************
 Validation Methods
 ******************/

 $.indicatorHideAll = function () {
    $('.indicator').hideAndPause();
 }

 $.indicatorStartAll = function () {
    $('.indicator').animationPlayStateRunning();
 }

 $.fn.hideAndPause = function () {
    return this.hidden().animationPlayStatePaused();
 }

 $.fn.indicatorShow = function () {
    // All indicators are started so that their 
    // play positions are all in sync
    $.indicatorStartAll();
    return this.visible().animationPlayStateRunning();
 }

 $.fn.indicatorHide = function () {
    return this.hideAndPause();
 }

 $.fn.assertRequired = function (desc, indicator, val) {
    indicator = indicator || $();
    val = val || this.val();

    indicator.indicatorHide();
    this.removeClass('invalid');

    if (_.isNull(val) || _.isUndefined(val) || _.isNaN(val) || $.trim(String(val)) == '') {
        indicator.indicatorShow();
        this.addClass('invalid');
        return desc + " is required. <br />";
    }
    return "";
 }

 $.fn.assertMinLength = function (length, desc, indicator, val) {
    indicator = indicator || $();
    val = val || this.val();

    indicator.indicatorHide();
    this.removeClass('invalid');

    if (val.length < length) {
        indicator.indicatorShow();
        this.addClass('invalid');
        return desc + " must be at least " + length + " characters.<br />";
    }
    return "";
}

$.fn.assertSyntaxEmail = function (indicator, val) {
    indicator = indicator || $();
    val = val || this.val();

    indicator.indicatorHide();
    this.removeClass('invalid');

    var reg_ex = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;

    if (!reg_ex.test(val)) {
        indicator.indicatorShow();
        this.addClass('invalid');
        return "The Email you entered appears to be invalid.<br />";
    }
    return "";
}

$.fn.assertEqual = function (desc1, other, desc2, indicator, val1) {
    indicator = indicator || $();
    val1 = val1 || this.val();

    indicator.indicatorHide();
    this.removeClass('invalid');

    var val1 = this.val();
    var val2 = other.val();

    if (val1 != val2) {
        indicator.indicatorShow();
        this.addClass('invalid');
        return desc1 + " and " + desc2 + " must match.<br />";
    }
    return "";
}

$.fn.assertAccepted = function (desc, indicator, val) {
    indicator = indicator || $();
    val = _.isUndefined(val) ? this.val() : val;

    indicator.indicatorHide();
    this.removeClass('invalid');

    if (!val) {
        indicator.indicatorShow();
        this.addClass('invalid');
        return "You must accept " + desc + ".<br />";
    }
    return "";
}

$.fn.assertChoice = function (desc, indicator, val) {
    indicator = indicator || $();
    val = _.isUndefined(val) ? this.val() : val;

    indicator.indicatorHide();
    this.removeClass('invalid');

    if (!val) {
        indicator.indicatorShow();
        this.addClass('invalid');
        return "You must choose a " + desc + ".<br />";
    }
    return "";
}

//--------------------------------------------
// assertExtension()
// Description: Asserts the file extension of the file to upload.
// Caustion:    if 'val' is blank, no validation is run, use assert_required 
//              prior to this function if 'val' should not be blank!
// Arguments:   exts - array of file extensions (periods included).
//                     pass in an empty array if all file extensions 
//                     are accepted.
//--------------------------------------------
$.fn.assertExtension = function(exts, indicator, val) {
    indicator = indicator || $();
    val = val || this.val();

    if (val.length == 0)
        return "";

    var valid = false;
    if (exts.length <= 0)
        valid = true;
    else {
        for (var i = 0; i < exts.length; i++) {
            if (val.endswith(exts[i])) {
                valid = true;
                break;
            }
        }
    }

    indicator.indicatorHide();
    this.removeClass('invalid');

    if (!valid) {
        indicator.indicatorShow();
        this.addClass('invalid');
        return "The file you chose to upload is of an invalid type.  File must be of type " + exts.join(" or ") + ".<br />";
    }
    return "";
}

$.fn.assertRegex = function (regex, failMessage, indicator, val) {
    indicator = indicator || $();
    val = val || this.val();

    indicator.indicatorHide();
    this.removeClass('invalid');

    if (!regex.test(val)) {
        indicator.indicatorShow();
        this.addClass('invalid');
        return failMessage;
    }
    return "";
}

$.fn.assertImageExtension = function (indicator, val) {
    indicator = indicator || $();
    val = val || this.val();
    return this.assertRegex(/.*\.(bmp|gif|jpg|jpe|jpeg|png)$/i, 'The image you chose to upload is of an invalid type. <br />', indicator, val);
}

$.fn.assertAudioExtension = function (indicator, val) {
    indicator = indicator || $();
    val = val || this.val();
    return this.assertRegex(/.*\.(mp3|ogg|wav)$/i, 'The track you chose to upload is of an invalid type. <br />', indicator, val);
}

/***************************
 Compound Validation Methods
 ***************************/

 $.fn.assertRequiredMinLength = function (length, desc, indicator, val) {
    indicator = indicator || $();
    val = val || this.val();
    var msg = this.assertRequired(desc, indicator, val);
    if (msg == "")
        msg = this.assertMinLength(length, desc, indicator, val);
    return msg;
}

$.fn.assertRequiredEqual = function (desc1, val2, desc2, indicator, val) {
    indicator = indicator || $();
    val = val || this.val();
    var msg = this.assertRequired(desc1, indicator, val);
    if (msg == "")
        msg = this.assertEqual(desc1, val2, desc2, indicator, val);
    return msg;
}

$.fn.assertRequiredSyntaxEmail = function (desc, indicator, val) {
    indicator = indicator || $();
    val = val || this.val();
    var msg = this.assertRequired(desc, indicator, val);
    if (msg == "")
        msg = this.assertSyntaxEmail(indicator, val);
    return msg;
}

$.fn.assertRequiredExtension = function (desc, exts, indicator, val) {
    indicator = indicator || $();
    val = val || this.val();
    var msg = this.assertRequired(desc, indicator, val);
    if (msg == "")
        msg = this.assertExtension(exts, indicator, val);
    return msg;
}

$.fn.assertRequiredImageExtension = function (desc, indicator, val) {
    indicator = indicator || $();
    val = val || this.val();
    var msg = this.assertRequired(desc, indicator, val);
    if (msg == "")
        msg = this.assertImageExtension(indicator, val);
    return msg;
}

$.fn.assertRequiredAudioExtension = function (desc, indicator, val) {
    indicator = indicator || $();
    val = val || this.val();
    var msg = this.assertRequired(desc, indicator, val);
    if (msg == "")
        msg = this.assertAudioExtension(indicator, val);
    return msg;
}