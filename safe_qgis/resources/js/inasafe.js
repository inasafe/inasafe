// from http://stackoverflow.com/a/4801719
(function($) {
    $.fn.goTo = function() {
        $('html, body').animate({
            scrollTop: $(this).offset().top + 'px'
        }, 'fast');
        return this; // for chaining...
    }
})(jQuery);

function hideTracebacks() {
  $('.traceback-detail').toggle();
}
