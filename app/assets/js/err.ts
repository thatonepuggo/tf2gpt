import $ from "./jquery.ts";
$(function () {
  let time_left = 5;

  const time_update = () => {
    if (time_left == 0) {
      $(".countdown").text("auto-refreshing...");
      return;
    }
    $(".countdown")
      .text(
        `auto-refreshing in ${time_left} second${time_left != 1 ? "s" : ""}...`,
      );
  };

  setInterval(function () {
    if (time_left == 0) {
      location.reload();
      return;
    }
    time_left--;
    time_update();
  }, 1000);
  time_update();
});
