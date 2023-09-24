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
    indlimit = parseInt(indlimit)
    $('input.slider-checkbox').on('change', function() {
        // Check how many inputs of class 'slider-checkbox' are checked.
        if( $('input.slider-checkbox:checked').length > indlimit) {
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
        var indexnumber = $('input.slider-checkbox:checked').length;
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

})(jQuery); // End of use strict