$( document ).ready(function() {
    $( "#register" ).click( function() {
      let params = {
        name: $("#name").val(),
        login: $("#login").val(),
        password: $("#password").val(),
      };

      query(params);
    });

    function query (params) {
      $.ajax({
        type: "POST",
        url: '/register',
        data: params, 
      })
      .done(function (res) {
        if ( res.error ) {
          $("#res").css({ color: 'red' }).html(res.error).addClass('hint');
        } else {
          $("#res").css({ color: 'green' }).html(res.success).addClass('hint');
        }
      })
      .fail(function () {
        console.log("fail");
      });
    };
  });