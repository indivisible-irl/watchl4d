
$(function () {
    showSpinner();
    pingChannels();
});

LIVE_CHANNEL = null;

function pingChannels () {
    $.ajax({
        url: '/watchl4d/live/', 
        type: 'GET',
        dataType: 'json',
        success: function (data, textStatus, jqXHR) {
            setLiveChannel(data);
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(textStatus, errorThrown);
        },
        complete: function (jqXHR, textStatus) {
            setTimeout(pingChannels, 10000);
        }
    });
}

/*
    Sets the current channel.
    If the channel is already live, this is a no-op.
    "data" - either a json structure or null.
*/
function setLiveChannel (data) {
    var oldc = LIVE_CHANNEL ? LIVE_CHANNEL['channel_name'] : null,
        newc = data ? data['channel_name'] : null;

    if (oldc && (oldc == newc)) {
        // Channel is already live: no-op
        return;
    }

    if (data) {
        hideSpinner();
        $('.title').text(data['title']);
        $('.provided-by').text(data['provided_by']);
        $('.channel-name').text('(' + data['channel_name'] + ')');
        $('.video-embed').html(data['video_embed']);
        $('.chat-embed').html(data['chat_embed']);
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
    });
}

function hideSpinner () {
    $('.spinner').animate({top: '-25%', opacity: 0}, 300, 'swing');
    $('.tryagain').animate({top: '-25%', opacity: 0}, 300, 'swing');
    $('.channel').animate({opacity: 100}, 300, 'swing');
}