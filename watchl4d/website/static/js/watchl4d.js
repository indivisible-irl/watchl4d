
TWITCH_WH_RATIO = 1.64;
HITBOX_WH_RATIO = 1.7;

LIVE_CHANNEL = null;
SELECTED_CHANNEL = null;
CHANNELS = {};

$(function () {
    $(window).resize(resizeVideo);

    resizeVideo();

    showSpinner();
    // Put a little delay to see if it helps embeded 
    // content from breaking upon load
    setTimeout(pingChannels, 2000);


    // $('.icon-refresh').bind('click', function (e) {
    //     setLiveChannel(LIVE_CHANNEL, true);
    // });
});

function resizeVideo () {

    var ratio = TWITCH_WH_RATIO;
    if ((LIVE_CHANNEL != null) && (LIVE_CHANNEL.channel_provider == 'hitbox.tv')) {
        ratio = HITBOX_WH_RATIO;
    }

    var widthDeduct = 320 + 170;
    var heightDeduct = 105 + 85;
    var minWidth = 350;
    var minHeight = 335;

    // TODO: Reserve 110px for header
    // Reserve 70px for
    var content = $('.content');

    var maxHeight = $('body').height() - heightDeduct;

    var desiredWidth = $('body').width() - widthDeduct;
    var desiredHeight = Math.floor(desiredWidth / ratio);

    if (desiredHeight > maxHeight) {
        desiredHeight = maxHeight;
        desiredWidth = Math.floor(desiredHeight * ratio);
    }

    if (desiredHeight < minHeight) {
        desiredHeight = minHeight;
        desiredWidth = Math.floor(desiredHeight * ratio);
    } 

    if (desiredWidth < minWidth) {
        desiredWidth = minWidth;
        desiredHeight = Math.floor(desiredWidth / ratio);
    }

    // if (desiredWidth )

    

    // var videoEmbed = $('.video-embed'),
    //     videoWidth = videoEmbed.width(),
    //     videoHeight = Math.floor(videoWidth / ratio);

    // //if (LIVE_CHANNEL == null) {
    //     videoWidth = content.width() - 340;
    //     videoHeight = Math.floor(videoWidth / ratio);
    // //}

    // if (videoHeight < 335) {
    //     videoHeight = 335;
    //     videoWidth = videoHeight * ratio;
    // }
    $('.video-embed').css('height', desiredHeight + 'px').css('width', desiredWidth + 'px');
    $('.chat-embed').css('height', desiredHeight + 'px').css('right', 'auto').css('left', 175 + desiredWidth);
    

    // var videoEmbed = $('.video-embed'),
    //     videoHeight = Math.floor(videoEmbed.width() / ratio);
    // $('.video-embed').css('height', videoHeight + 'px').css('width', videoWidth + 'px');

    // $('.chat-embed').css('height', videoHeight + 'px');
}

function pingChannels () {
    $.ajax({
        url: Settings.ROOT_URL + 'live/', 
        type: 'GET',
        dataType: 'json',
        success: function (data, textStatus, jqXHR) {
            // Hide menu spinner
            $('.spinner-small').css('display', 'none');
            // Update Channels
            CHANNELS = data;
            updateChannelStatus();
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(textStatus, errorThrown);
        },
        complete: function (jqXHR, textStatus) {
            setTimeout(pingChannels, 10000);
        }
    });
}

function updateChannelStatus () {
    var liveChannel = null,
        featuredChannel = null,
        twitchChannels = $('.twitch-channels'),
        hitboxChannels = $('.hitbox-channels');

    twitchChannels.empty();
    hitboxChannels.empty();

    for (var i = 0; i < CHANNELS.length; i++) {
        var channel = CHANNELS[i];

        var classes = "row ";
        if (channel.live) {
            classes += "live ";
        }
        if (SELECTED_CHANNEL && SELECTED_CHANNEL.channel_name == channel.channel_name) {
            if (channel.live) {
                classes += "selected";
            }
            else {
                SELECTED_CHANNEL = null;
            }
        }

        var el = $('<div class="' + classes + '" data-channel-name="' + channel.channel_name + '">');

        el.append('<span>' + channel.channel_name + '</span>');

        if (channel.live) {
            el.append('<span class="icon icon-live"></span>');
            el.append('<span>' + channel.viewers + '</span>');
            el.append('<div class="sub-row channel-title">' + channel.title + '</div>');

            el.bind('click', function (e) {
                var row = $(e.currentTarget),
                    channel_name = row.attr('data-channel-name');

                $('.selected').removeClass('selected');
                $('[data-channel-name="' + channel_name + '"]').addClass('selected');

                if (CHANNELS == null) {
                    return;
                }
                for (var i = 0; i < CHANNELS.length; i++) {
                    if (CHANNELS[i].channel_name == channel_name) {
                        SELECTED_CHANNEL = CHANNELS[i];
                        setLiveChannel(SELECTED_CHANNEL);
                        return;
                    }
                }
            });
        }

        if (channel.channel_provider == 'twitch.tv') {
            twitchChannels.append(el);
        }
        else {
            hitboxChannels.append(el);
        }

        if (liveChannel == null && channel.live) {
            liveChannel = channel;
        }
        
        if ((featuredChannel == null && channel.live) || (featuredChannel != null && (featuredChannel.viewers < channel.viewers))) {
            featuredChannel = channel;
        }
    }

    // Show or Hide the feature channel depending on if there is one
    if (featuredChannel) {
        $('.featured-channel').text(featuredChannel.channel_name);
        $('.featured-row')
            .slideDown()
            .attr('data-channel-name', featuredChannel.channel_name)
            .bind('click', function (e) {
                var row = $(e.currentTarget),
                    channel_name = row.attr('data-channel-name');
                
                $('.selected').removeClass('selected');
                $('[data-channel-name="' + channel_name + '"]').addClass('selected');

                var channel_name = row.attr('data-channel-name');
                if (CHANNELS == null) {
                    return;
                }
                for (var i = 0; i < CHANNELS.length; i++) {
                    if (CHANNELS[i].channel_name == channel_name) {
                        SELECTED_CHANNEL = CHANNELS[i];
                        setLiveChannel(SELECTED_CHANNEL);
                    }
                }
            });

        $('[data-channel-name="' + featuredChannel.channel_name + '"]').addClass('selected');
        liveChannel = featuredChannel;

    }
    else {
         $('.featured-row').slideUp();
    }

    if (SELECTED_CHANNEL) {
        liveChannel = SELECTED_CHANNEL;
    }

    var liveChannelIsGone = false;
    if (LIVE_CHANNEL != null) {
        for (var i = 0; i < CHANNELS.length; i++) {
            var channel = CHANNELS[i];
            if (channel.channel_name == LIVE_CHANNEL.channel_name) {
                if (!channel.live) {
                    liveChannelIsGone == true;
                }
                break;
            }
        }
    }

    if ((LIVE_CHANNEL == null) || (liveChannelIsGone)) {
        setLiveChannel(liveChannel);
    }
}

/*
    Sets the current channel.
    If the channel is already live, this is a no-op.
    "data" - either a json structure or null.
*/
function setLiveChannel (data, force) {
    var oldc = LIVE_CHANNEL ? LIVE_CHANNEL['channel_name'] : null,
        newc = data ? data['channel_name'] : null,
        force = typeof force == 'undefined' ? false : force;

    var already_loaded = (!force && oldc && (oldc == newc));

    if (data) {
        hideSpinner();
        $('.title').text(data['title']);
        $('.provided-by').text(data['provided_by']);
        $('.channel-name').text('(' + data['channel_provider'] + '/' + data['channel_name'] + ')');
        if (!already_loaded) {
            $('.video-embed').html(data['video_embed']);
            $('.chat-embed').html(data['chat_embed']);
            resizeVideo();
        }
        $('.viewers').text(data['viewers']);
    }
    else {
        showSpinner();
    }

    LIVE_CHANNEL = data;
}


function showSpinner () {
    $('.spinner').animate({top: '25%', opacity: 100}, 300, 'swing');
    $('.channel').animate({opacity: 0}, 300, 'swing', function () {
        $('.title').empty();
        $('.provided-by').empty();
        $('.channel-name').empty();
        $('.video-embed').empty();
        $('.chat-embed').empty();
        $('.viewers').empty();
        $('.content').css('margin-right', '0px');
    });
    $('.chat-embed').animate({opacity: 0}, 300, 'swing');
}

function hideSpinner () {
    $('.spinner').animate({top: '-25%', opacity: 0}, 300, 'swing');
    $('.channel').animate({opacity: 100}, 300, 'swing');
    $('.chat-embed').animate({opacity: 100}, 300, 'swing');
    // $('.content').css('margin-right', '318px');
}