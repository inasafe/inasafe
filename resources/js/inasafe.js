// from http://stackoverflow.com/a/4801719
 $(document).ready(function(){
	 $(".container > img:first-child").wrap( "<div class='branding'></div>" );
 });

(function($) {
    $.fn.goTo = function() {
        $('html, body').animate({
            scrollTop: $(this).offset().top + 'px'
        }, 'fast');
        return this; // for chaining...
    }
})(jQuery);

function toggleTracebacks() {
  $('.traceback-detail').toggle();
}

