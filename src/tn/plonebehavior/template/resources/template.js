;(function($) {
  $(function() {
    $('iframe.templated-page-view').each(function() {
      var $frame = $(this);
      var $doc = $frame.contents();
      $doc.ready(function() { $frame.height($doc.find('html').height()); });
    });
  });
})(jQuery);
