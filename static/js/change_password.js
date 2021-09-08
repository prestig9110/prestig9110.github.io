$( document ).ready(function() {
    $( "#change_password" ).click( function() {
        let params = {
            password: $("#password").val(),
          };
    
          query(params);
    });

    function query (params) {
        $.ajax({
          type: "POST",
          url: '/change_password',
          data: params, 
        })
        .done(function (res) {
            if ( res.error ) {
                $("#mess").css({ color: 'red' }).html(res.error).addClass('hint');
            } else {
                $("#mess").css({ color: 'green' }).html(res.ok).addClass('hint');
            }
        });
    };
});