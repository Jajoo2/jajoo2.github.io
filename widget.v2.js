/*
    Version: 3.0
    Date: 2023-04-11
*/
function addCommas(nStr){
    nStr += '';
    var x = nStr.split('.');
    var x1 = x[0];
    var x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1)) {
        x1 = x1.replace(rgx, '$1' + ',' + '$2');
    }
    return x1 + x2;
}
    
const js_url = document.getElementById('howlongaogog_js').src;
let full_url = (new URL(js_url));

protocol = full_url.protocol;
domain = full_url.hostname;
port = full_url.port;

new_url = protocol + '//' + domain;

if (port !== '') {
    new_url += ':' + port;
}

if (howlongagogo_options.preview === true) {
    preview = true;
} else {
    preview = false;
}

function loadView(howlongagogo_options) {

    const users_date = new Date(howlongagogo_options.date);
    const formattedDate = users_date.toLocaleDateString();

    const container = document.getElementById("timeago_container");
    var html_markup = 
        '<link rel="stylesheet" href="' + new_url + '/css/widget-v2/countdown.css" />' +
        '<link rel="stylesheet" href="' + new_url + '/css/widget-v2/main.css" />' +
        '<style>' +
            '#timeago_container, #howlongagogo_p {background-color: ' + (howlongagogo_options.bg_color ? addHashIfNeeded(howlongagogo_options.bg_color) : '#fff') +'}' +
            '#timeago_container .subheading, #howlongagogo_p, #howlongagogo_p a {color: ' + (howlongagogo_options.bg_color ? addHashIfNeeded(howlongagogo_options.name_color) : '#212529') + '}' +
            '#timeago_container .date_time_span {color: ' + (howlongagogo_options.bg_color ? addHashIfNeeded(howlongagogo_options.name_color) : '#212529') + '}' +
            '#timeago_container .date_span {color: ' + (howlongagogo_options.bg_color ? addHashIfNeeded(howlongagogo_options.date_color) : '#212529') + '}' +
        '</style>' +
        '<p class="subheading">' + howlongagogo_options.name + '</p>';

    if (howlongagogo_options.show_date === true) {
        html_markup += 
            '<p class="date_time_span" data-toggle="tooltip" data-placement="bottom" title="Timezone:">' +
                formattedDate +
                (howlongagogo_options.time !== '00:00:00' ? ' at ' + howlongagogo_options.time.split(':').slice(0, 2).join(':') : '')  +
            '</p>';
    }

    html_markup += '<div class="d-flex">' +
                        '<div class="flex-fill date_span countdown_days_accurate_html" id="countdown_days_accurate_html"><strong>&nbsp;</strong><br/>&nbsp;</div>' +
                        '<div class="flex-fill date_span countdown_hours_html" id="countdown_hours_html"><strong>&nbsp;</strong><br/>&nbsp;</div>' +
                        '<div class="flex-fill date_span countdown_seconds_html" id="countdown_minutes_html"><strong>&nbsp;</strong><br/>&nbsp;</div>' +
                        '<div class="flex-fill date_span countdown_seconds_html" id="countdown_seconds_html"><strong>&nbsp;</strong><br/>&nbsp;</div>' +
                    '</div>';

    html_markup += '<img class="d-none" src="' + new_url + '/iframe/track?name=widget_v2&url=' + encodeURIComponent(window.location.href) + '&preview=' + preview + '" width="1" height="1" />';

    container.innerHTML = html_markup;
}

function addHashIfNeeded(str) {
    if (str.charAt(0) !== '#') {
      str = '#' + str;
    }
    return str;
}

function doesLinkBackExist() {

    const ourLinkBackHref = document.querySelector('a[href="' + new_url + '"]');

    const links = document.querySelectorAll('a');
    let ourLinkBackText = false;
    links.forEach(link => {
    if (link.textContent.includes('howlongagogo.com')) {
        ourLinkBackText = true;
        return;
    }
    });

    if (ourLinkBackHref === null || ourLinkBackText === false) {

        const linkElement = document.createElement('link');
        linkElement.rel = 'stylesheet';
        linkElement.type = 'text/css';
        linkElement.href = new_url + '/css/widget-v2/main.css';

        document.head.appendChild(linkElement);

        var new_markup = "<p id='no_link_back'>Please remember to include the link back to <strong>https://howlongagogo.com</strong> as per the widget and our T&C's."
        document.getElementById("timeago_container").innerHTML = new_markup;

        return true;
    }
    return true;
}

if (doesLinkBackExist()) {
    loadView(howlongagogo_options);

    if (typeof howlongagogo_options.offset === 'undefined') {
        offset = '';
    } else {
        offset = howlongagogo_options.offset;
    }
    
   

    if (typeof multiply_hours_by_days === 'undefined') {
        multiply_hours_by_days = null
    }

    // Set the local date and time
    const localDate = new Date();

    //const targetDate = howlongagogo_options.date + "T" + howlongagogo_options.time + "+01:00"; // set the custom end date and time in the specified format
    const targetDate = howlongagogo_options.date + "T" + howlongagogo_options.time + offset; // set the custom end date and time in the specified format

    // Parse the target date into a Date object
    const targetDateObj = new Date(targetDate);

    // Calculate the time difference between the two dates
    const timeDifference = targetDateObj.getTime() - localDate.getTime();

    // Set up the countdown timer
    let countdown = timeDifference / 1000; // Convert milliseconds to seconds
    const countdownTimer = setInterval(() => {

        // Calculate the remaining time in hours, minutes, and seconds
        let days, hours, minutes, seconds;
        if (timeDifference < 0) {
            days = Math.floor(Math.abs(countdown) / 86400);
            hours = Math.floor((Math.abs(countdown) % 86400) / 3600);
            minutes = Math.floor((Math.abs(countdown) % 3600) / 60);
            seconds = Math.floor(Math.abs(countdown) % 60);
        } else {
            days = Math.floor(countdown / 86400);
            hours = Math.floor((countdown % 86400) / 3600);
            minutes = Math.floor((countdown % 3600) / 60);
            seconds = Math.floor(countdown % 60);
        }

        // Format DAYS output
        if (days != 0) {
            countdown_days_accurate_html = '<strong>' + addCommas(days) + '</strong><br />days';
        } else {
            countdown_days_accurate_html = '<strong>0</strong><br />days';
        }

        // Format HOURS output
        if (multiply_hours_by_days && days > 0) {
            countdown_hours_html = '<strong>' + addCommas(hours + ((days) * 24)) + '</strong><br /> hours';
        } else {
            countdown_hours_html = '<strong>' + addCommas(hours) + '</strong><br /> hours';
        }

        // Format MINUTES output
        countdown_minutes_html = '<strong>' + addCommas(minutes) + '</strong><br /> mins';

        // Format SECONDS output
        countdown_seconds_html = '<strong>' + addCommas(seconds) + '</strong><br /> secs';

        document.getElementById('countdown_days_accurate_html').innerHTML = countdown_days_accurate_html;
        document.getElementById('countdown_hours_html').innerHTML = countdown_hours_html;
        document.getElementById('countdown_minutes_html').innerHTML = countdown_minutes_html;
        document.getElementById('countdown_seconds_html').innerHTML = countdown_seconds_html;

        // Update the countdown display
        //console.log(`${days}d ${hours}h ${minutes}m ${seconds}s`);

        // Decrement the countdown by one second
        countdown--;
    }, 1000); // Update the countdown every second
}
