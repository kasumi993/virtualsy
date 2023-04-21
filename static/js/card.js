(function($) {
    "use strict";
    $(document).ready(function() {
        $(".machine").click(function() {
            if (!$(this).find(".radio").hasClass("locked")) {
                $(".machine").removeClass("selected");
                $(this).addClass("selected");
            }
        });
    });
})(jQuery);