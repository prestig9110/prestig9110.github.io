$(document).ready(function () {
    // Получить консультацию
    $(".register-btn").on("click", function (event) {
      event.preventDefault();
      $(".modal-register").fadeIn(350);
      
    });
    // Закрыть получение консультации
    $(".register-close").on("click", function (event) {
      event.preventDefault();
      $(".modal-register").fadeOut(350);
    });
  });