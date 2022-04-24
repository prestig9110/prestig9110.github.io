$( document ).ready(function() {
    let clicked = false;

    $( "[id^=accept-], [id^=not_accept-], [id^=ban-], [id^=unban-], [id^=del_wl-], [id^=delete-], [id^=add_wl-]" ).click( function() {
        if (clicked === false) {
            clicked = true;
            id = $(this)[0].id.match(/^(\w+)-(\d+)$/);

            let params = {
            id: id[2],
            action: id[1],
            username: $("#username-" + id[2]).text()
            };

            if ( !proverka() ) return;

            change_user(params);
        }
    });

    function change_user (params) {
        $.ajax({
            type: "POST",
            url: '/change_user',
            data: params
        })
        .done(function (res) {
            alert(res.message)
            clicked = false;
            location.reload()
        })
        .fail(function () {
            clicked = false;
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

    var content = {};

    $( "[id^=acord-]" ).click( function() {
        id = $(this)[0].id.match(/^(\w+)-(\d+)$/);

        if (content[id[2]]) {
            return;
        }

        let params = {
            id: id[2],
        };

        list_players(params);
    });

    function list_players (params) {
        $.ajax({
            type: "POST",
            url: '/list_players/',
            data: params
        })
        .done(function (res) {
            content[params.id] = "exist";

            usersResult = JSON.parse(JSON.stringify(res.usersResult));

            html = `<table id="metki" class="metki">
                        <thead>
                            <tr>
                                <th>Username</th>
                                <th>email</th>
                                <th>Возраст</th>
                                <th>Действия</th>
                                <th>Действия</th>
                                <th>Действия</th>
                            </tr>
                        </thead>
                        <tbody id="metki_tbody">\n`

            usersResult[params.id].forEach(function(us) {
                html = html + `
                    <tr>
                        <th id="username-${us.id}" data-label=" ">${us.username}</th>
                        <th data-label=" ">${us.email}</th>
                        <th data-label=" ">${us.age}</th>\n`

                        if (us.status == 2) {
                            html = html + `
                                <th data-label=" "><button id="ban-${us.id}">Забанить</button></th>
                                <th data-label=" "><button id="del_wl-${us.id}">Удалить из ВЛ</button></th>
                                <th data-label=" "><button id="delete-${us.id}">Удалить</button></th>\n`
                        } else if (us.status == 3) {
                            html = html + `
                                <th data-label=" "><button id="accept-${us.id}">Принять</button></th>
                                <th data-label=" "><button id="delete-${us.id}">Удалить</button></th>\n`
                        } else if (us.status == 4) {
                            html = html + `
                                <th data-label=" "><button id="unban-${us.id}">Разбанить</button></th>
                                <th data-label=" "><button id="delete-${us.id}">Удалить</button></th>\n`
                        } else if (us.status == 5) {
                            html = html + `
                                <th data-label=" "><button id="add_wl-${us.id}">Добавить в ВЛ</button></th>
                                <th data-label=" "><button id="delete-${us.id}">Удалить</button></th>\n`
                        }
                html = html + '</tr>'
            })
                            
            html = html + '</tbody>\n</table>'

            $("#content-" + params.id).html(html);

            $( "[id^=accept-], [id^=not_accept-], [id^=ban-], [id^=unban-], [id^=del_wl-], [id^=delete-], [id^=add_wl-]" ).on( 'click', function() {
                id = $(this)[0].id.match(/^(\w+)-(\d+)$/);
        
                let params = {
                  id: id[2],
                  action: id[1],
                  username: $("#username-" + id[2]).text()
                };

                if ( !proverka() ) return;
        
                change_user(params);
            });
        })
        .fail(function () {
            alert("fail");
        });
    };
});