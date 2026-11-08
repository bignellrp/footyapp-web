/*!
    * Start Bootstrap - Grayscale v6.0.3 (https://startbootstrap.com/theme/grayscale)
    * Copyright 2013-2020 Start Bootstrap
    * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-grayscale/blob/master/LICENSE)
    */
    (function ($) {
    "use strict"; // Start of use strict

    // Smooth scrolling using jQuery easing
    $('a.js-scroll-trigger[href*="#"]:not([href="#"])').click(function () {
        if (
            location.pathname.replace(/^\//, "") ==
                this.pathname.replace(/^\//, "") &&
            location.hostname == this.hostname
        ) {
            var target = $(this.hash);
            target = target.length
                ? target
                : $("[name=" + this.hash.slice(1) + "]");
            if (target.length) {
                $("html, body").animate(
                    {
                        scrollTop: target.offset().top - 70,
                    },
                    1000,
                    "easeInOutExpo"
                );
                return false;
            }
        }
    });

    // Closes responsive menu when a scroll trigger link is clicked
    $(".js-scroll-trigger").click(function () {
        $(".navbar-collapse").collapse("hide");
    });

    // Activate scrollspy to add active class to navbar items on scroll
    $("body").scrollspy({
        target: "#mainNav",
        offset: 100,
    });

    // Collapse Navbar
    var navbarCollapse = function () {
        if ($("#mainNav").offset().top > 100) {
            $("#mainNav").addClass("navbar-shrink");
        } else {
            $("#mainNav").removeClass("navbar-shrink");
        }
    };
    // Collapse now if page is not at top
    navbarCollapse();
    // Collapse the navbar when page is scrolled
    $(window).scroll(navbarCollapse);
    
    // Custom Validation Code

    // Index Checkbox Limit & Autosave
    let indlimit = $('#players').text();
    indlimit = parseInt(indlimit);
    $('input.slider-checkbox').on('change', function() {
        // The Auto screen squad (playing + reserves) has its own handler below.
        if ($(this).hasClass('squad-checkbox')) { return; }
        // Check how many inputs of class 'slider-checkbox' are checked and do not have the [data-limit="exclude"] attribute.
        if( $('input.slider-checkbox:checked:not([data-limit="exclude"])').length > indlimit) {
            this.checked = false;
        }

        // Count Index Checkboxes that are checked
        var indexnumber = $('input.slider-checkbox:checked:not([data-limit="exclude"])').length;
        $('.indextotalchecked').html(indlimit - indexnumber);

        // Collect all checked checkbox values for autosave
        var checkedPlayers = [];
        $('input.slider-checkbox:checked').each(function() {
            checkedPlayers.push($(this).val());
        });

        // Send AJAX POST request to /autosave
        $.ajax({
            url: '/autosave',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ available_players: checkedPlayers }),
            success: function(response) {
                console.log('Autosaved successfully:', response);
            },
            error: function(xhr, status, error) {
                console.error('Autosave failed:', error);
            }
        });
    });

    // Auto screen: first N ticks play, the next 5 are reserves (tick order), further ticks are blocked.
    var $squadForm = $('#squad-form');
    if ($squadForm.length) {
        var squadLimit = parseInt($('#players').text(), 10);
        var maxReserves = parseInt($('#max-reserves').text(), 10);
        var squad = { playing: [], reserves: [] };
        try {
            var saved = JSON.parse($('#squad-order').val() || '{}');
            squad.playing = saved.playing || [];
            squad.reserves = saved.reserves || [];
        } catch (e) { /* start empty */ }

        var renderSquad = function() {
            $('input.squad-checkbox').each(function() {
                var name = $(this).val();
                var reserveIndex = squad.reserves.indexOf(name);
                var $container = $(this).closest('.slider-container');
                var $inner = $container.find('.slider-inner');
                $container.toggleClass('is-reserve', reserveIndex >= 0);
                if (reserveIndex >= 0) { $inner.attr('data-reserve', reserveIndex + 1); }
                else { $inner.removeAttr('data-reserve'); }
                this.checked = reserveIndex >= 0 || squad.playing.indexOf(name) >= 0;
            });
            $('.indextotalchecked').text(Math.max(0, squadLimit - squad.playing.length));
            $('#reserve-count').text(squad.reserves.length);
            $('#squad-order').val(JSON.stringify(squad));
        };

        $('input.squad-checkbox').on('change', function() {
            var name = $(this).val();
            var $message = $('#squad-message').hide();
            if (this.checked) {
                if (squad.playing.length < squadLimit) {
                    squad.playing.push(name);
                } else if (squad.reserves.length < maxReserves) {
                    squad.reserves.push(name);
                } else {
                    this.checked = false;
                    $message.text('Squad is full (' + squadLimit + ' playing + ' + maxReserves + ' reserves).').show();
                    return;
                }
            } else if (squad.playing.indexOf(name) >= 0) {
                // A playing player dropped out: reserve 1 is promoted and the rest move up.
                squad.playing = squad.playing.filter(function(n) { return n !== name; });
                if (squad.reserves.length) { squad.playing.push(squad.reserves.shift()); }
            } else {
                squad.reserves = squad.reserves.filter(function(n) { return n !== name; });
            }
            renderSquad();
            $.ajax({
                url: '/autosave',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ squad: squad }),
                success: function(response) { console.log('Autosaved successfully:', response); },
                error: function(xhr) {
                    console.error('Autosave failed:', xhr.status);
                    if (xhr.status === 400 && xhr.responseJSON) { $message.text(xhr.responseJSON.message).show(); }
                }
            });
        });
        renderSquad();
    }

    // Compare Team A Checkbox Limit

    let compalimit = $('#compplayers').text();
    compalimit = parseInt(compalimit)
    $('input.slider-checkbox-a').on('change', function() {
        // Check how many inputs of class 'single-checkbox' are checked.
        if( $('input.slider-checkbox-a:checked').length > compalimit) {
            this.checked = false;
        }
    });

    // Compare Team B Checkbox Limit

    let compblimit = $('#compplayers').text();
    compblimit = parseInt(compblimit)
    $('input.slider-checkbox-b').on('change', function() {
        // Check how many inputs of class 'single-checkbox' are checked.
        if( $('input.slider-checkbox-b:checked').length > compblimit) {
            this.checked = false;
        }
    });

    // Count Compare A Checkboxes that are checked

    $('input.slider-checkbox-a').on('change', function() {
        var companumber = $('input.slider-checkbox-a:checked').length;
        $('.compatotalchecked').html(compalimit - companumber);
    });

    // Count Compare B Checkboxes that are checked

    $('input.slider-checkbox-b').on('change', function() {
        var compbnumber = $('input.slider-checkbox-b:checked').length;
        $('.compbtotalchecked').html(compblimit - compbnumber);
    });

    // Change Image with dropdown

    $('#changeImageA').change(function(){
        $('#imageA')[0].src = "/static/"+this.value+".png";
    });

    // Change Image with dropdown

    $('#changeImageB').change(function(){
        $('#imageB')[0].src = "/static/"+this.value+".png";
    });

    // Confirm delete

    const postButton = document.getElementById('postButton');

    if (postButton) {
        postButton.addEventListener('click', function() {
        const confirmation = confirm("Are you sure you want to delete this player. There is no recovery option for their stats?");

        if (confirmation) {
            // user clicked OK, proceed with posting
            // insert your code here for posting the data
            console.log("Posting...");
        } else {
            // user clicked Cancel, do nothing
            console.log("Cancelled.");
        }
        });
    }

    // Display status messages from URL parameters
    // This function is called automatically on page load
    document.addEventListener('DOMContentLoaded', function() {
        const urlParams = new URLSearchParams(window.location.search);
        const error = urlParams.get('error');
        const success = urlParams.get('success');
        
        if (error || success) {
            // Display the message
            alert(error || success);
            // Clean URL to remove parameters
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    });

})(jQuery); // End of use strict