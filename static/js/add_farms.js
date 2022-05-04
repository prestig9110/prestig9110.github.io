$( document ).ready(function() {
    $( "#add" ).click( function() {
      let params = {
        server: $("#add_server").val(),
        name: $("#add_name").val(),
        x: $("#add_x").val(),
        y: $("#add_y").val(),
        z: $("#add_z").val(),
        action: "add"
      };

      $("#add_name, #add_x, #add_y, #add_z").val('');

      queryADD(params);
    });

    function queryADD (params) {
      $.ajax({
        type: "POST",
        url: '/farm_manager',
        data: params, 
      })
      .done(function (res) {
        if ( res.error ) {
          $("#add_marker_res").css({ color: 'red' }).html(res.error).addClass('hint');
        } else {
        //   $("#add_marker_res").css({ color: 'green' }).html(res.success).addClass('hint');
          if ( params.action != 'edit' ) {
            var table = document.getElementById( 'metki_tbody' );
            row = table.insertRow(0);
            cell1 = row.insertCell(0).outerHTML = '\
              <th>\
                <select name="server" id="server-' + res.success + '">\
                  <option value="gmgame"' + ( params.server == 'gmgame' ? 'selected="selected"' : '' ) + '>Основной мир</option>\
                  <option value="farm"' + ( params.server == 'farm' ? 'selected="selected"' : '' ) + '>Фермерский мир</option>\
                </select>\
              </th>';
            cell2 = row.insertCell(1).outerHTML = '<th><input type="text" placeholder="' + params.name + '" name="name" id="name-' + res.success + '" value="' + params.name + '"></th>';
            cell3 = row.insertCell(2).outerHTML = '<th><input type="text" placeholder="' + params.x + '" name="x" id="x-' + res.success + '" value="' + params.x + '"></th>';
            cell4 = row.insertCell(3).outerHTML = '<th><input type="text" placeholder="' + params.y + '" name="y" id="y-' + res.success + '" value="' + params.y + '"></th>';
            cell5 = row.insertCell(4).outerHTML = '<th><input type="text" placeholder="' + params.z + '" name="z" id="z-' + res.success + '" value="' + params.z + '"></th>';
            cell6 = row.insertCell(5).outerHTML = '<th><button id="edit-' + res.success + '">Изменить</button></th>';
            cell7 = row.insertCell(6).outerHTML = '<th><button id="del-' + res.success + '">Удалить</button></th>';

            row.setAttribute("id", "tr-" + res.success);
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
                name: $("#name-" + res.success).val(),
                x: $("#x-" + res.success).val(),
                y: $("#y-" + res.success).val(),
                z: $("#z-" + res.success).val(),
                action: "edit",
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
          id: id[1],
          action: "del"
        };

        if ($("#opUser").data()) params.allmarkers = 1;
        
        if ( !proverka() ) return;
  
        queryDEL(params);
    });

    function queryDEL (params) {
        $.ajax({
            type: "POST",
            url: '/farm_manager',
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
          name: $("#name-" + id[1]).val(),
          x: $("#x-" + id[1]).val(),
          y: $("#y-" + id[1]).val(),
          z: $("#z-" + id[1]).val(),
          action: "edit",
          markerID: id[1]
        };

        if ( !proverka() ) return;
  
        queryADD(params);
    });

    function proverka() {
      if (confirm("Подтвердить")) {
          return true;
      } else {
          return false;
      }
    }; 

    $( "#reinit" ).click( function() {
        let params = {
          action: "reinit"
        };

        if ( !proverka() ) return;
  
        $.ajax({
            type: "POST",
            url: '/farm_manager',
            data: params
        })
        .done(function (res) {
            alert("Служба перезапущена")
        })
        .fail(function () {
            alert("Не удалось перезапустить службу")
        });
    });
});