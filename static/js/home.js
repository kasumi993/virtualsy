(function($) {
    "use strict";
    $(document).ready(function() {
        // set the conditions per user
        const user = JSON.parse(localStorage.getItem('user'));
        $('#title').text(`Welcome ${user.name}`);
        $('#credit').text(`Remaining Credits: ${user.credit}`);
        if (user.credit === 0) {
            $('.machine .radio').addClass('locked');
            $('.connect-form-bgbtn').addClass('disabled');
            $('.connect-form-btn').prop('disabled', true);
        } else if (user.credit <= 100) {
            $(".machine .radio:not(#linux .radio)").addClass("locked");
        } else if (user.credit > 100) {
          $("#other .radio").addClass("locked");
        }

        // listening to connect button click

        $(".connect-form-btn").click(function() {
            // Check if at least one .machine element has class 'selected'
            if ($(".machine.selected").length > 0) {
                window.location.href = "/azure?vm=" + $(".machine.selected").attr('id');
              
            } else {
              alert("Please choose at least one option.");
            }
        });



        // function to retreive the url parameters

        $.urlParam = function(name) {
          var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
          if (results == null) {
            return null;
          }
          else {
            return decodeURI(results[1]) || 0;
          }
        }
    });
})(jQuery);