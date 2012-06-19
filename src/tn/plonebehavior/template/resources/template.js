;(function($) {
  $(window).load(function() {
    $('iframe.templated-page-view').each(function() {
      var $frame = $(this);
      $frame.height($frame.contents().find('html').height());
    });
  });
})(jQuery);
