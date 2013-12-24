$(document).ready(function() {
  function refit() {
    var headerWidth = $('#header').width();
    $('.title').width(headerWidth - 34);
    $('.link div').width(headerWidth - 34);
    $('.thumbnail').width(headerWidth);
    $('.crop').width(headerWidth);
    $('.crop img').width(headerWidth);
    $('.item img').each(function() {
      if (!$(this).parent().hasClass('crop')) {
        $(this).css('max-width', headerWidth - 40);
        $(this).css('max-height', headerWidth - 40);
      }
    });
  }
  refit();
  
  function linkClippedImage() {
    var parent = $(this).parent();
    if (parent.hasClass('crop') || parent.is('a'))
      return;

    var newImg = $(this).clone();
    newImg.removeAttr('width');
    newImg.css('max-width', '');
    newImg.removeAttr('height');
    newImg.css('max-height', '');
    newImg.css('display', 'none');
    $('body').append(newImg);
    var width = newImg.width();
    var height = newImg.height();
    if (width == 0) {
      width = this.naturalWidth;
    }
    if (height == 0) {
      height = this.naturalHeight;
    }
    newImg.remove();

    if (width > this.width || height > this.height) {
      $(this).wrap('<a href="' + this.src + '" />');
    }
  }

  $('.item img').load(linkClippedImage);
  
  $(window).resize(function() {
    refit();
    $('.item img').each(linkClippedImage);
  });

  $('.rollover').hover(
    function() {
      this.src = this.src.replace('-off', '-on');
    },
    function() {
      this.src = this.src.replace('-on', '-off');
    }
  );

  $('.link').hover(
    function() {
      var img = $(this).find('img.thumbnail')[0];
      img.src = img.src.replace('-off', '-on');
      $(img).css('-moz-box-shadow', '0px 0px 10px 4px rgb(136, 136, 136)');
      $(img).css('-webkit-box-shadow', '0px 0px 10px 4px rgb(136, 136, 136)');
      $(img).css('box-shadow', '0px 0px 10px 4px rgb(136, 136, 136)');
    },
    function() {
      var img = $(this).find('img.thumbnail')[0];
      img.src = img.src.replace('-on', '-off');
      $(img).css('-moz-box-shadow', '0px 0px 10px 2px rgb(136, 136, 136)');
      $(img).css('-webkit-box-shadow', '0px 0px 10px 2px rgb(136, 136, 136)');
      $(img).css('box-shadow', '0px 0px 10px 2px rgb(136, 136, 136)');
    }
  );

  $('a.back').click(
    function(e) {
      e.preventDefault();
      window.history.back();
    }
  );

  $('a.confirm').click(
    function(e) {
      e.preventDefault();
      if (confirm('Really?')) {
        // Send delete request and reload page
        $.post(this.href, {}, function() { location.reload(true); });
      }
    }
  );

}); 
