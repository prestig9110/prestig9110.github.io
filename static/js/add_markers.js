$( document ).ready(function() {
    $( "#add" ).click( function() {
      let params = {
        server: $("#add_server").val(),
        id_type: $("#add_id_type").val(),
        name: $("#add_name").val(),
        x: $("#add_x").val(),
        y: $("#add_y").val(),
        z: $("#add_z").val(),
        description: $("#add_description").val()
      };

      queryADD(params);
    });

    function queryADD (params) {
      $.ajax({
        type: "POST",
        url: '/add_marker',
        data: params, 
      })
      .done(function (res) {
        if ( res.error ) {
          $("#add_marker_res").css({ color: 'red' }).html(res.error).addClass('hint');
        } else {
        //   $("#add_marker_res").css({ color: 'green' }).html(res.success).addClass('hint');
          if ( !params.edit ) {
            var table = document.getElementById( 'metki_tbody' ),
            row = table.insertRow(0),
            cell1 = row.insertCell(0),
            cell2 = row.insertCell(1);
            cell3 = row.insertCell(2);
            cell4 = row.insertCell(3);
            cell5 = row.insertCell(4);
            cell6 = row.insertCell(5);
            cell7 = row.insertCell(6);
            cell8 = row.insertCell(7);
            cell9 = row.insertCell(8);

            cell1.innerHTML = '<select name="server" id="server-' + res.success + '"><option value="gmgame"' + ( params.server == 'gmgame' ? 'selected="selected"' : '' ) + '>Основной мир</option><option value="farm"' + ( params.server == 'farm' ? 'selected="selected"' : '' ) + '>Фермерский мир</option></select>';
            cell2.innerHTML = '<select name="id_type" id="id_type-' + res.success + '"><option value="basePlayers"' + ( params.id_type == 'basePlayers' ? 'selected="selected"' : '' ) + '>Базы игроков</option><option value="city"' + ( params.id_type == 'city' ? 'selected="selected"' : '' ) + '>Города</option></select>';
            cell3.innerHTML = '<input type="text" placeholder="' + params.name + '" name="name" id="name-' + res.success + '" value="' + params.name + '">';
            cell4.innerHTML = '<input type="text" placeholder="' + params.x + '" name="x" id="x-' + res.success + '" value="' + params.x + '">';
            cell5.innerHTML = '<input type="text" placeholder="' + params.y + '" name="y" id="y-' + res.success + '" value="' + params.y + '">';
            cell6.innerHTML = '<input type="text" placeholder="' + params.z + '" name="z" id="z-' + res.success + '" value="' + params.z + '">';
            cell7.innerHTML = '<input type="text" placeholder="' + params.description + '" name="description" id="description-' + res.success + '" value=' + params.description + '></input>';
            cell8.innerHTML = '<button id="edit-' + res.success + '">Изменить</button>';
            cell9.innerHTML = '<button id="del-' + res.success + '">Удалить</button>';
          }

          $(document).on("click" , "#del-" + res.success , function() {
            let params = {
                id: res.success
            };
        
            queryDEL(params)

            $(this).parent().parent().remove();
          } );

          $(document).on("click" , "#edit-" + res.success , function() {
            let paramsUpdate = {
                server: $("#server-" + res.success).val(),
                id_type: $("#id_type-" + res.success).val(),
                name: $("#name-" + res.success).val(),
                x: $("#x-" + res.success).val(),
                y: $("#y-" + res.success).val(),
                z: $("#z-" + res.success).val(),
                description: $("#description-" + res.success).val(),
                edit: 1,
                markerID: res.success
            };
        
            queryADD(paramsUpdate);
          } );
        }
      })
      .fail(function () {
        console.log("fail");
      });
    };

    $( "[id^=del-]" ).click( function() {
        id = $(this)[0].id.match(/^del-(\d+)$/);

        let params = {
          id: id[1]
        };
  
        queryDEL(params);
    });

    function queryDEL (params) {
        console.log(params);
        $.ajax({
            type: "POST",
            url: '/del_marker',
            data: params
        })
        .done(function (res) {
            $('#metki_tbody').find('tr#tr-' + params.id).remove();
        })
        .fail(function () {
            console.log("fail");
        });
    };

    $( "[id^=edit-]" ).click( function() {
        id = $(this)[0].id.match(/^edit-(\d+)$/);

        let params = {
          server: $("#server-" + id[1]).val(),
          id_type: $("#id_type-" + id[1]).val(),
          name: $("#name-" + id[1]).val(),
          x: $("#x-" + id[1]).val(),
          y: $("#y-" + id[1]).val(),
          z: $("#z-" + id[1]).val(),
          description: $("#description-" + id[1]).val(),
          edit: 1,
          markerID: id[1]
        };
  
        queryADD(params);
    });
  });