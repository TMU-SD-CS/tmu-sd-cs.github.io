$(function(){
  var pageTop = $("#page-top");
  pageTop.hide();
  pageTop.click(function () {
    $('body, html').animate({ scrollTop: 0 }, 500);
    return false;
  });
  $(window).scroll(function () { 
    if($(this).scrollTop() >= 200) {
      pageTop.fadeIn();
    } else {
      pageTop.fadeOut();
    }
  });
});

$(function() {
    $('body').find('img').parent('a').addClass('no_icon');
})

$(function(){
    var timer = false;
    var prewidth = $(window).width()
    $(window).resize(function() {
        if (timer !== false) {
            clearTimeout(timer);
        }
        timer = setTimeout(function() {
            var nowWidth = $(window).width()
            if(prewidth !== nowWidth){
                location.reload();
            }
            prewidth = nowWidth;
        }, 200);
    });
});