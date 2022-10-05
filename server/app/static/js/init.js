function timer_count_down(timeout_sec) {

    function updateClock() {

        var t = parseInt($('#time-sec').text());

        if (t <= 0) {
            $('#time-sec').text('0');
            clearInterval(timeinterval);

            // reminder
            M.toast({html: "time out!"});
        } else {
            $('#time-sec').text((t - 1).toString());
        }
    }

    $('#time-sec').text(timeout_sec.toString());
    var timeinterval = setInterval(updateClock, 1000);

}

function socketio_init () {
    const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', function () {
        console.log("connection success");
    });

    socket.on('disconnect', function () {
        console.log("connection success");
    });

    socket.on('error', function (err) {
        console.error("getting error");
    });

    // console.log()l;
    socket.on('query', function (msg) {
        // assign value to search more
        $('#search-more').attr("href", "http://www.google.com/search?q=" + msg.data.query);

        $('#query').val(msg.data.query);
        $('#deviceId').val(msg.data.deviceId);
        $('#requestId').val(msg.data.requestId);
        $('#sessionId').val(msg.data.sessionId);

        // reset the timer to 10 second
        timer_count_down(10);
        M.updateTextFields();
    });
}

function get_wolFrame (question) {
    // TODO: some encoding of the
    $.ajax({
        url: "http://api.wolframalpha.com/v1/conversation.jsp?appid=9JG323-YVHU5YE5HT&i=" + question
    });
}

function button_submit_response () {
    $.ajax({
        url: location.protocol + "//" + location.host + "/api/response",
        cache: false,
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
            "request_id": $('#requestId').val(),
            "speech": $('#speech').val(),
            "card_title": $('#card-title').val(),
            "card_content": $('#card-content').val()
        }, null, '\t'),
        success: (res, status, xhr) => {
            M.toast({html: 'OK!'});
        },
        error: (xhr, status, error) => {
            console.error("error: " + (xhr.status + ': ' + xhr.statusText));
            M.toast({html: 'Error!'});
        },
        complete: function(response, status, xhr) {
            console.log("Finished!");
        }
    });
}

// start a new search
// TODO: move to the chrome extension
function search(query) {
    url ='http://www.google.com/search?q=' + query;
    window.open(url,'_blank');
}

$(document).ready(function () {
    socketio_init();
});