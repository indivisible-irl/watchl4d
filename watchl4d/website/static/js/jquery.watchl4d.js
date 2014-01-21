/******************
 Validation Methods
 ******************/

 $.fn.assertRequiredSyntaxSteamId = function (indicator, val, desc) {
    indicator = indicator || $();
    val = val || this.val();
    desc = desc || "Steam ID";

    indicator.indicatorHide();
    this.removeClass('invalid');

    var reg_ex = /^STEAM_[0-9]:[0-9]:[0-9]+$/;

    if (!reg_ex.test(val)) {
        indicator.indicatorShow();
        this.addClass('invalid');
        return desc + " is invalid.<br />";
    }
    return "";
}