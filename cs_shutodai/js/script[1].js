$( function() {
  var $body = $('body');
  var ua = navigator.userAgent.toLowerCase();

  // anchor link
  function anchorLink() {
    $(document).on('click', 'a[href^="#"]', function(e) {
      e.preventDefault();

      var $el     = $(this);
      var $target = $($el.attr('href'));
      var paddingTop = 70;

      if (!$target[0]) {
        return;
      }

      var offset = $target.offset().top;
      $('html, body').animate({scrollTop: offset - paddingTop});
    });
  }

  function navControl() {
    var $navBtn = $('#js-navBtn');
    var $nav = $('#js-nav');

    $navBtn.on('click', function() {
      if ( $navBtn.hasClass('is-open') ) {
        $nav.fadeOut(300);
      } else {
        $nav.fadeIn(300);
      }
      $navBtn.toggleClass('is-open');
      $body.toggleClass('nav-open');
    });

    $('body').on('click', function() {
      if ( $navBtn.hasClass('is-open') ) {
        $nav.fadeOut(300);
        $navBtn.toggleClass('is-open');
        $body.toggleClass('nav-open');
      }
    });

    $('#js-nav, #js-navBtn').on( 'click', function(e) {
      e.stopPropagation();
    });

  }

  function pagePluginCode(w, winW) {
    // 幅に応じて高さを変更する場合
    if (winW > 768) {
      var h = $('.c-teacherList').height();
    } else {
      var h = 400;
    }
    return '<div class="fb-page" data-href="https://www.facebook.com/%E9%A6%96%E9%83%BD%E5%A4%A7%E5%AD%A6%E6%9D%B1%E4%BA%AC-%E6%83%85%E5%A0%B1%E7%A7%91%E5%AD%A6%E7%A7%91%E6%83%85%E5%A0%B1%E7%A7%91%E5%AD%A6%E5%9F%9F-502499453485187/" data-tabs="timeline" data-width="'+ w +'" data-height="'+ h +'" data-small-header="true" data-adapt-container-width="true" data-hide-cover="true" data-show-facepile="true"><blockquote cite="https://www.facebook.com/%E9%A6%96%E9%83%BD%E5%A4%A7%E5%AD%A6%E6%9D%B1%E4%BA%AC-%E6%83%85%E5%A0%B1%E7%A7%91%E5%AD%A6%E7%A7%91%E6%83%85%E5%A0%B1%E7%A7%91%E5%AD%A6%E5%9F%9F-502499453485187/" class="fb-xfbml-parse-ignore"><a href="https://www.facebook.com/%E9%A6%96%E9%83%BD%E5%A4%A7%E5%AD%A6%E6%9D%B1%E4%BA%AC-%E6%83%85%E5%A0%B1%E7%A7%91%E5%AD%A6%E7%A7%91%E6%83%85%E5%A0%B1%E7%A7%91%E5%AD%A6%E5%9F%9F-502499453485187/">首都大学東京　情報科学科・情報科学域</a></blockquote></div>';
  }

  // ページプラグインを追加する要素
  var facebookWrap = $('#js-fbPage');
  var fbBeforeWidth = ''; // 前回変更したときの幅
  var fbWidth = facebookWrap.width(); // 今回変更する幅
  var fbTimer = false;
  function fbPagePlugin() {
    if (fbTimer !== false) {
      clearTimeout(fbTimer);
    }
    fbTimer = setTimeout(function() {
      winW = $(window).width();
      fbWidth = Math.floor(facebookWrap.width()); // 変更後の幅を取得
      // 前回の幅から変更があった場合のみ処理
      if(fbWidth != fbBeforeWidth) {
        facebookWrap.html(pagePluginCode(fbWidth, winW)); // ページプラグインのコード変更
        window.FB.XFBML.parse(); // ページプラグインの再読み込み
        fbBeforeWidth = fbWidth; // 今回変更分を保存しておく
      }
    }, 200);
  }

  // fire when DOM is ready
  $(function() {
    anchorLink();
    navControl();
  });

  // fire when page is fully loaded
  $(window).on('load',function(){
  });

  $(window).on('load resize',function(){
    fbPagePlugin();
  });

});
