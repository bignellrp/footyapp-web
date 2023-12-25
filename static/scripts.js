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

    // Custom slider functionality
    // Function to initialize sliders
    function initSliders() {
        const sliders = document.querySelectorAll('.custom-slider');

        sliders.forEach(slider => {
            slider.addEventListener('click', function() {
                toggleSliderState(this);
            });
            // Set the initial state of the slider based on its class
            updateSliderState(slider);
        });
    }

    // Function to toggle the state of a slider
    function toggleSliderState(slider) {
        let newState;
        if (slider.classList.contains('playing')) {
            slider.classList.remove('playing');
            slider.classList.add('benched');
            newState = 'BENCHED';
        } else if (slider.classList.contains('benched')) {
            slider.classList.remove('benched');
            slider.classList.add('none');
            newState = 'NONE';
        } else {
            slider.classList.remove('none');
            slider.classList.add('playing');
            newState = 'PLAYING';
        }
        updateSliderState(slider);

        // Update the value of the corresponding hidden input field
        const inputField = document.getElementById(slider.getAttribute('data-input-id'));
        if (inputField) {
            inputField.value = newState;
        }
    }

    // Function to update the visual state of the slider
    function updateSliderState(slider) {
        const handle = slider.querySelector('.slider-handle');
        if (slider.classList.contains('playing')) {
            handle.style.left = '2px'; // Position for 'PLAYING'
        } else if (slider.classList.contains('benched')) {
            handle.style.left = 'calc(50% - 13px)'; // Position for 'BENCHED'
        } else {
            handle.style.left = 'calc(100% - 30px)'; // Position for 'NONE'
        }
    }

    // Initialize sliders when the document is ready
    $(document).ready(function() {
        initSliders();
    });

})(jQuery); // End of use strict