$( document ).ready(function() {
    $( "[id^=accept-], [id^=not_accept-], [id^=ban-], [id^=unban-], [id^=del_wl-]" ).click( function() {
        id = $(this)[0].id.match(/^(\w+)-(\d+)$/);

        let params = {
          id: id[2],
          action: id[1],
          username: $("#username-" + id[2]).text()
        };

        if ( !proverka() ) return;

        change_user(params);
    });

    function change_user (params) {
        $.ajax({
            type: "POST",
            url: '/change_user',
            data: params
        })
        .done(function (res) {
            alert(res.message)
            location.reload()
        })
        .fail(function () {
            console.log("fail");
        });
    };

    function proverka() {
        if (confirm("Подтвердить")) {
            return true;
        } else {
            return false;
        }
      }; 
});