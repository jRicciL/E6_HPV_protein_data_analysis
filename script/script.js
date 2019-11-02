
$(document).ready(function(){
	$('#scriptAD4').load("fuentes/adt4-omica.py");

	var height = $(window).height();
	var openMenu = false;

    //Abrir cerrar menú
    $('#menu_icon').on('click', function() {
    	if (openMenu == false){
	    	$('.sidebar').css({"left": 0});
	    	$('#menu_icon').css({"left": 15.1 + "%"});
	    	$('#contenido').css({"margin-left": 15 + "%"});
	    	openMenu = true;
    	}
    	else if (openMenu == true){
	    	$('.sidebar').css({"left": (-15.1) + "%"});
	    	$('#menu_icon').css({"left": 0 });
	    	$('#contenido').css({"margin-left": 0 + "%"});

	    	openMenu = false;
    	}
    	reposition();
    });

	var offset = $('div#presentacion').outerHeight()*1.5,
	offset_opacity = 1200,
	scroll_top_duration = 700,
	$back_to_top = $('.cd-top');

	function ajustesIniciales(){
		$("section#body").css({"margin-top": height/2 + 150 + "px"});
	}

	

	var moveTitle = function(a){
		var scrollTop = $(this).scrollTop(); //Calcula los pixeles hacia arriba de la imagen
		var pixels = $('div#presentacion').outerHeight()*1.5;
		if(scrollTop > pixels){
			$("section#titulo1").css({
				"top": - (scrollTop - pixels)
			});
		}
		else if(scrollTop <= pixels){
			$("section#titulo1").css({
				"top": 0
			});
		}
	}

	var moveMenu = function(a){
		var scrollTop = $(this).scrollTop(); //Calcula los pixeles hacia arriba de la imagen
		var pixels =  $('div#presentacion').outerHeight()*1.5;
		var pixels2 = $('#titulo1').outerHeight() - (scrollTop - pixels)
		if(scrollTop > pixels ){
			$(".sidebar").css({
				"top": - (scrollTop - pixels) + $('#titulo1').outerHeight()
			});
			$('#menu_icon').css({
				'top': - (scrollTop - pixels) + $('#titulo1').outerHeight()
			});
			if( pixels2 < 0){
				$(".sidebar").css({
					"top": 0
				});
				$('#menu_icon').css({'top': 0 });

			}

		}

		else if(scrollTop <= pixels){
			$(".sidebar").css({
				"top": $('#titulo1').outerHeight()
			});
			$('#menu_icon').css({
				'top': $('#titulo1').outerHeight()
			});
		}
	}

	//Reposiciona el div de presentación
	var reposition = function(){
		var top = $('#titulo1').outerHeight();
		$('div#presentacion').css({'margin-top': top });
    	//if ($(this).scrollTop() < $('div#presentacion').outerHeight()*1.5) {
    		moveMenu();
    		moveTitle();
			//$('#menu_icon').css({'margin-left': $('.sidebar').position().left + $('.sidebar').outerWidth() });
    	//}
	}
    reposition();
    

	$(document).scroll( function(){
		reposition();
		( $(this).scrollTop() > offset ) ? $back_to_top.addClass('cd-is-visible') : $back_to_top.removeClass('cd-is-visible cd-fade-out');
		if( $(this).scrollTop() > offset_opacity ) { 
			$back_to_top.addClass('cd-fade-out');
		}
	});

	$('.top').on('click', function(event){
		event.preventDefault();
		$('body,html').animate({
			scrollTop: 0 ,
		 	}, scroll_top_duration
		);
	});


	var resizeText = function () {
		// Standard height, for which the body font size is correct
		var preferredFontSize = 100; // %
		var preferredSize = 1024 * 768;

		var currentSize = $(window).width() * $(window).height();
		var scalePercentage = Math.sqrt(currentSize) / Math.sqrt(preferredSize);
		var newFontSize = preferredFontSize * scalePercentage;
		$("body").css("font-size", newFontSize + '%');
	};

	$(window).bind('resize', function() {
		resizeText();
		reposition();

	}).trigger('resize');


});