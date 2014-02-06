
$(function () {
    showSpinner();
    // Put a little delay to see if it helps embeded 
    // content from breaking upon load
    setTimeout(pingChannels, 2000);

    $('.icon-refresh').bind('click', function (e) {
        setLiveChannel(LIVE_CHANNEL, true);
    });
});

LIVE_CHANNEL = null;
SELECTED_CHANNEL = null;
CHANNELS = {};

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

    setLiveChannel(liveChannel);
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
    });
}

function hideSpinner () {
    $('.spinner').animate({top: '-25%', opacity: 0}, 300, 'swing');
    $('.tryagain').animate({top: '-25%', opacity: 0}, 300, 'swing');
    $('.channel').animate({opacity: 100}, 300, 'swing');
}