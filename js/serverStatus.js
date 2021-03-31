//based on a pen by @robinselmer
var url = "https://api.minetools.eu/ping/mine.gmgame.ru/25565";

$.getJSON(url, function (r) {
   //data is the JSON string
   if (r.error) {
      $("#rest").html("Server Offline");
      return false;
   }
   var pl = "";
   if (r.players.sample.length > 0) {
      pl = "<br>OP: " + r.players.sample[0].name;
   }
   $("#rest").html(
      r.description.replace(/§(.+?)/gi, "") +
      "<br><b>Версия: Yatopia 1.16.4 - 1.16.5 </b> " +
      "<br><b>Режим игры: Выживание </b> " +
      "<br><b>Игроков онлайн: </b> " +
      r.players.online +
      pl +
      "<b> из 55</b> "
   );
   $("#favicon").attr("src", r.favicon);
});
