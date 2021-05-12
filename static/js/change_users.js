$( document ).ready(function() {
    $( "[id^=accept-], [id^=not_accept-], [id^=ban-], [id^=unban-]" ).click( function() {
        id = $(this)[0].id.match(/^(\w+)-(\d+)$/);

        let params = {
          id: id[2],
          action: id[1]
        };

        console.log(params)

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
});