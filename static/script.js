$(document).ready(function() {
  $("div.link").hover(
    function() {
      var img = $(this).find("img.thumbnail")[0];
      img.src = img.src.replace("-off", "-on");
      $(img).css("box-shadow", "0px 0px 10px 4px rgb(136, 136, 136)");
    },
    function() {
      var img = $(this).find("img.thumbnail")[0];
      img.src = img.src.replace("-on", "-off");
      $(img).css("box-shadow", "0px 0px 10px 2px rgb(136, 136, 136)");
  });
}); 