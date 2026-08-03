$(function(){

	// ヘッダー固定の場合、ヘッダーの高さ、もしくはずらしたい分の数値を指定
	var hd_height = 0;

	////// ページトップ //////
	$('#pt').click(function(){
		click_scroll_pagetop();
	});

	let topBtn = $('#pt');
	topBtn.hide();
	//スクロールが100に達したらボタン表示
	$(window).scroll(function () {
		if ($(this).scrollTop() > 100) {
			topBtn.fadeIn();
		} else {
			topBtn.fadeOut();
		}
	});

	////// 外部ページブランク //////
	$("a[href^='http://'] , a[href^='https://']").not("a[href*='" + location.hostname + "']").attr("target","_blank");
	$("a[href$='.pdf']").attr("target","_blank");

	////// スライドパネル //////
	$(".js_sld_pnl").click(function(){
		var str_active = "active";
		var slide_panel_id = $(this).attr("data-sld_pnl");
		slide_panel_id = $("#"+slide_panel_id);
		slide_panel_id.stop().slideToggle().toggleClass(str_active);
		if(slide_panel_id.hasClass(str_active)){
			var sld_pnl_text = $(this).attr("data-sld_pnl_cls");
			$(this).text(sld_pnl_text);
		}else{
			var sld_pnl_text_02 = $(this).attr("data-sld_pnl_opn");
			$(this).text(sld_pnl_text_02);
		}
		return false;
	});
	$(".js_sld_pnl").each(function() {
		var sld_pnl_opn = $(this).attr("data-sld_pnl_opn");
		$(this).text(sld_pnl_opn);
	});

	////// タブパネル //////
	$(".js_tab_pnl").click(function(){
		var slide_panel_id = $(this).attr("data-tab_pnl");
		$(".tab_pnl.active").removeClass("active");
		$("#"+slide_panel_id).addClass("active");
		$(".js_tab_pnl.active").removeClass("active");
		$(this).addClass("active");
		return false;
	});

	////// ページ内リンク //////
	if (window.matchMedia('(max-width: 1024px)').matches) {
		// ページ外アンカーのページ付きリンクへのスムーススクロール
		var urlHash = location.hash;
		if(urlHash) {
			$('body,html').stop().scrollTop(0);
			setTimeout(function(){
				var target = $(urlHash);
				var position = target.offset().top - 20;
				$('body,html').stop().animate({scrollTop:position}, 500);
			}, 100);
		}

		// ページ内アンカーのページ付きリンクへのスムーススクロール
		$(function(){
			$('a[href*="#"], area[href*="#"]').not(".noScroll").click(function() {

				var speed = 400, // ミリ秒(この値を変えるとスピードが変わる)
					href = $(this).prop("href"), //リンク先を絶対パスとして取得
					hrefPageUrl = href.split("#")[0], //リンク先を絶対パスについて、#より前のURLを取得
					currentUrl = location.href, //現在のページの絶対パスを取得
					currentUrl = currentUrl.split("#")[0]; //現在のページの絶対パスについて、#より前のURLを取得

				//#より前の絶対パスが、リンク先と現在のページで同じだったらスムーススクロールを実行
				if(hrefPageUrl == currentUrl){

					//リンク先の#からあとの値を取得
					href = href.split("#");
					href = href.pop();
					href = "#" + href;

					//スムースクロールの実装
					var target = $(href == "#" || href == "" ? 'html' : href),
						position = target.offset().top - 20; //targetの位置を取得
						$('body,html').stop().animate({scrollTop:position}, 500);

					return false;
				}
			});
		});

	} else if (window.matchMedia('(min-width:1025px)').matches) {

		// ページ外アンカーのページ付きリンクへのスムーススクロール
		var urlHash = location.hash;
		if(urlHash) {
			$('body,html').stop().scrollTop(0);
			setTimeout(function(){
				var target = $(urlHash);
				var position = target.offset().top - hd_height;
				$('body,html').stop().animate({scrollTop:position}, 500);
			}, 100);
		}

		// ページ内アンカーのページ付きリンクへのスムーススクロール
		$(function(){
			$('a[href*="#"], area[href*="#"]').not(".noScroll").click(function() {

				var speed = 400, // ミリ秒(この値を変えるとスピードが変わる)
					href = $(this).prop("href"), //リンク先を絶対パスとして取得
					hrefPageUrl = href.split("#")[0], //リンク先を絶対パスについて、#より前のURLを取得
					currentUrl = location.href, //現在のページの絶対パスを取得
					currentUrl = currentUrl.split("#")[0]; //現在のページの絶対パスについて、#より前のURLを取得

				//#より前の絶対パスが、リンク先と現在のページで同じだったらスムーススクロールを実行
				if(hrefPageUrl == currentUrl){

					//リンク先の#からあとの値を取得
					href = href.split("#");
					href = href.pop();
					href = "#" + href;

					//スムースクロールの実装
					var target = $(href == "#" || href == "" ? 'html' : href),
						position = target.offset().top - hd_height; //targetの位置を取得
						$('body,html').stop().animate({scrollTop:position}, 500);

					return false;
				}
			});
		});
	}

	//サイドナビ自動生成
	auto_list("#auto_list",".mcon h2");

	////// レスポンシブ //////
	// spナビ用開閉ボタン
	$(".sp_nav_trigger").click(function () {
		$(this).toggleClass("sp_active");
		$(".nav").toggleClass("sp_nav_open");
	});

	// hdでsrcset属性が指定されたとき
	var $hd_logo_img = $(".hd_logo img")
	var hd_logo_img_srcset = $hd_logo_img.attr("srcset");
	if(hd_logo_img_srcset && is_ie()){
		$(window).on('resize load',function(){
			var hd_logo_img_srcset_02 = hd_logo_img_srcset.replace(/,\s/g,',');
			var hd_logo_img_src_ary = hd_logo_img_srcset_02.split(',');
			var hd_logo_img_src = hd_logo_img_src_ary[0].split(' ')[0];
			var sp_hd_logo_img_src = hd_logo_img_src_ary[1].split(' ')[0];
			// PC環境の場合
			if (window.matchMedia( '(min-width: 770px)' ).matches) {
				$hd_logo_img.attr("src",hd_logo_img_src);
			// sp環境の場合
			} else {
				$hd_logo_img.attr("src",sp_hd_logo_img_src);
			}
		});
	}

});

// マウスオーバー
function hover_change_img(obj_name){
	var postfix = '-ov';
	$(obj_name).find('a img').not('[src*="'+ postfix +'."]').each(function() {
		var img = $(this);
		var src = img.attr('src');
		var src_ov = src.substr(0, src.lastIndexOf('.'))
		+ postfix
		+ src.substring(src.lastIndexOf('.'));
		$('<img>').attr('src', src_ov);
		img.hover(function() {
			img.attr('src', src_ov);
		}, function() {
			img.attr('src', src);
		});
	});
}

// ページトップ
function click_scroll_pagetop(){
	var top = $(window).scrollTop();//スクロール値取得
	var speed = 4;//速度
	var time = Math.floor(top/speed);//小数点切り捨て
	$('body,html').animate({
		scrollTop: 0
	},time);
	return false;
}

//サイドナビ自動生成
function auto_list(element,target) {
		var $element     = $(element);
		var $target_list = $(target);
		if($target_list.size() > 0){
			$target_list.each(function(i) {
				var $current = $(this),
					head_text = $current.text();
				$current.attr("id", "anker-" + i);
				$element.append("<li><a href='#anker-" + i + "'>" + head_text + "</a></li>");
			});
			return false;
		}else {
			$element.css("display","none");
		}
};

$('.child_wrap_btn').on('click', function() {//タイトル要素をクリックしたら
	var findElm = $(this).next(".child_wrap");//直後のアコーディオンを行うエリアを取得し
	$(findElm).slideToggle();//アコーディオンの上下動作

	if($(this).hasClass('close')){//タイトル要素にクラス名closeがあれば
		$(this).removeClass('close');//クラス名を除去し
	}else{//それ以外は
		$(this).addClass('close');//クラス名closeを付与
	}
});

//ユーザーエージェント IE
var user_agent = navigator.userAgent.toLowerCase();
var app_version = navigator.appVersion.toLowerCase();
function is_ie(){
	// IE(11以外)
	var is_msie = (user_agent.indexOf('msie') > -1) && (user_agent.indexOf('opera') == -1);
	// IE11
	var is_ie11 = (user_agent.indexOf('trident/7') > -1);
	// Edge
	var is_edge = (user_agent.indexOf('edge') > -1);
	if(is_msie || is_ie11 || is_edge){ return true; }else{ return false; }
}

//ユーザーエージェント Google Chrome
function is_chrome(){
	return (user_agent.indexOf('chrome') > -1) && (user_agent.indexOf('edge') == -1);
}
//ユーザーエージェント firefox
function is_firefox(){
	return (user_agent.indexOf('firefox') > -1);
}
//ユーザーエージェント safari
function is_safari(){
	var user_agent = navigator.userAgent.toLowerCase();
	return (user_agent.indexOf('safari') > -1) && (user_agent.indexOf('chrome') == -1);
}
