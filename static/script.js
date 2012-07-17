$(document).ready(function() {
  $("div.link").hover(
    function() {
      var img = $(this).find("img.thumbnail")[0];
      img.src = img.src.replace("-off", "-on");
      $(img).css("box-shadow", "0 0 6px 6px rgb(136, 136, 136)");
    },
    function() {
      var img = $(this).find("img.thumbnail")[0];
      img.src = img.src.replace("-on", "-off");
      $(img).css("box-shadow", "0 0 5px 5px rgb(136, 136, 136)");
  });
}); 