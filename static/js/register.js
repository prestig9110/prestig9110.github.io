$( document ).ready(function() {
    $( "#register" ).click( function() {
      let params = {
        password: $("#password").val(),
        login: $("#login").val(),
        type: $("#type").val(),
        age: $("#age").val(),
        from_about: $("#from_about").val(),
        you_about: $("#you_about").val(),
        servers: $("#servers").val()
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
          location.reload()
        }
      })
      .fail(function () {
        console.log("fail");
        location.reload()
      });
    };
  });