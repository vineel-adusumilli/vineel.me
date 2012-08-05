$(document).ready(function() {
  $("img.rollover").hover(
    function() {
      this.src = this.src.replace("-off", "-on");
    },
    function() {
      this.src = this.src.replace("-on", "-off");
    }
  );

  $("div.link").hover(
    function() {
      var img = $(this).find("img.thumbnail")[0];
      img.src = img.src.replace("-off", "-on");
      $(img).css("-moz-box-shadow", "0px 0px 10px 4px rgb(136, 136, 136)");
      $(img).css("-webkit-box-shadow", "0px 0px 10px 4px rgb(136, 136, 136)");
      $(img).css("box-shadow", "0px 0px 10px 4px rgb(136, 136, 136)");
    },
    function() {
      var img = $(this).find("img.thumbnail")[0];
      img.src = img.src.replace("-on", "-off");
      $(img).css("-moz-box-shadow", "0px 0px 10px 2px rgb(136, 136, 136)");
      $(img).css("-webkit-box-shadow", "0px 0px 10px 2px rgb(136, 136, 136)");
      $(img).css("box-shadow", "0px 0px 10px 2px rgb(136, 136, 136)");
    }
  );

  $("div.item img").load(function () {
    var newImg = $(this).clone();
    newImg.removeAttr("width");
    newImg.removeAttr("height");
    $(newImg).css("display", "none");
    $("body").append(newImg);
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
  });
}); 
