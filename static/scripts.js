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

    // Index Checkbox Limit
    let indlimit = $('#players').text();
    indlimit = parseInt(indlimit);
    $('input.slider-checkbox').on('change', function() {
        // Check how many inputs of class 'slider-checkbox' are checked and do not have the [data-limit="exclude"] attribute.
        if( $('input.slider-checkbox:checked:not([data-limit="exclude"])').length > indlimit) {
            this.checked = false;
        }
    });

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

    // Count Index Checkboxes that are checked

    $('input.slider-checkbox').on('change', function() {
        // use :checked:not([data-limit="exclude"]) to exclude checkboxes with data-limit="exclude"
        var indexnumber = $('input.slider-checkbox:checked:not([data-limit="exclude"])').length;
        $('.indextotalchecked').html(indlimit - indexnumber);
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

    // Reset Season functionality
    const resetSeasonBtn = document.getElementById('resetSeasonBtn');
    if (resetSeasonBtn) {
        resetSeasonBtn.addEventListener('click', function() {
            const confirmation = confirm("WARNING: This will download a backup and reset ALL season data. Are you sure you want to continue?");
            
            if (confirmation) {
                // Disable button to prevent multiple clicks
                resetSeasonBtn.disabled = true;
                resetSeasonBtn.textContent = 'Creating backup...';
                
                // Create a hidden form to submit POST request
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/reset_season';
                form.style.display = 'none';
                document.body.appendChild(form);
                
                // Create an iframe to handle the download
                const iframe = document.createElement('iframe');
                iframe.name = 'downloadFrame';
                iframe.style.display = 'none';
                document.body.appendChild(iframe);
                form.target = 'downloadFrame';
                
                // Submit form to trigger download
                form.submit();
                
                // Wait for download to start, then confirm reset
                setTimeout(function() {
                    resetSeasonBtn.textContent = 'Resetting database...';
                    
                    // Call the confirm endpoint to reset the database
                    fetch('/reset_season_confirm', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        const messageDiv = document.getElementById('resetMessage');
                        if (data.success) {
                            messageDiv.innerHTML = '<h3 style="color: green;">' + data.message + '</h3>';
                            messageDiv.style.display = 'block';
                            setTimeout(function() {
                                window.location.reload();
                            }, 2000);
                        } else {
                            messageDiv.innerHTML = '<h3 style="color: red;">Error: ' + data.error + '</h3>';
                            messageDiv.style.display = 'block';
                            resetSeasonBtn.disabled = false;
                            resetSeasonBtn.textContent = 'Reset Season';
                        }
                    })
                    .catch(error => {
                        const messageDiv = document.getElementById('resetMessage');
                        messageDiv.innerHTML = '<h3 style="color: red;">Error: Failed to reset database</h3>';
                        messageDiv.style.display = 'block';
                        resetSeasonBtn.disabled = false;
                        resetSeasonBtn.textContent = 'Reset Season';
                        console.error('Error:', error);
                    });
                }, 1000); // Wait 1 second for download to start
                
                // Cleanup
                setTimeout(function() {
                    document.body.removeChild(form);
                    document.body.removeChild(iframe);
                }, 5000);
            }
        });
    }

})(jQuery); // End of use strict