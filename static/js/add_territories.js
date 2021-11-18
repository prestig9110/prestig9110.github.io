$( document ).ready(function() {
    $( "#add" ).click( function() {
      let params = {
        name: $("#name-add").val(),
        xStart: $("#xStart-add").val(),
        zStart: $("#zStart-add").val(),
        xStop: $("#xStop-add").val(),
        zStop: $("#zStop-add").val(),
        world: $("#world-add").val()
      };

      if ( !proverka() ) return;

      queryADD(params);
    });

    function queryADD (params) {
      $.ajax({
        type: "POST",
        url: '/add_territories',
        data: params, 
      })
      .done(function (res) {
        if ( res.error ) {
          $("#add_marker_res").css({ color: 'red' }).html(res.error).addClass('hint');
        } else {
        //   $("#add_marker_res").css({ color: 'green' }).html(res.success).addClass('hint');
          if ( !params.edit ) {
            var table = document.getElementById( 'metki_tbody' );
            row = table.insertRow(0);
            cell1 = row.insertCell(0).outerHTML = '<th><input type="text" placeholder="' + params.name + '" name="name" id="name-' + res.success + '" value="' + params.name + '"></th>';
            cell2 = row.insertCell(1).outerHTML = '\
              <th>\
                <select name="world" id="world' + res.success + '">\
                  <option value="' + params.world + '"' + ( params.world == 'gmgame' ? 'selected="selected"' : '' ) + '>Основной</option>\
                  <option value="' + params.world + '"' + ( params.world == 'farm' ? 'selected="selected"' : '' ) + '>Фермерский</option></select>\
                </select>\
              </th>';
            cell3 = row.insertCell(2).outerHTML = '<th><input type="text" placeholder="' + params.xStart + '" name="xStart" id="xStart-' + res.success + '" value="' + params.xStart + '"></th>';
            cell4 = row.insertCell(3).outerHTML = '<th><input type="text" placeholder="' + params.zStart + '" name="zStart" id="zStart-' + res.success + '" value="' + params.zStart + '"></th>';
            cell5 = row.insertCell(4).outerHTML = '<th><input type="text" placeholder="' + params.xStop + '" name="xStop" id="xStop-' + res.success + '" value="' + params.xStop + '"></th>';
            cell6 = row.insertCell(5).outerHTML = '<th><input type="text" placeholder="' + params.zStop + '" name="zStop" id="zStop-' + res.success + '" value="' + params.zStop + '"></th>';
            cell7 = row.insertCell(6).outerHTML = '<th><button id="edit-' + res.success + '">Изменить</button></th>';
            cell8 = row.insertCell(7).outerHTML = '<th><button id="del-' + res.success + '">Удалить</button></th>';

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
                name: $("#name-" + res.success).val(),
                xStart: $("#xstart-" + res.success).val(),
                zStart: $("#zStart-" + res.success).val(),
                xStop: $("#xStop-" + res.success).val(),
                zStop: $("#zStop-" + res.success).val(),
                world: $("#world-" + res.success).val(),
                edit: 1,
                markerID: res.success
            };

            if ( !proverka() ) return;
        
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
        
        if ( !proverka() ) return;

        queryDEL(params);
    });

    function queryDEL (params) {
        $.ajax({
            type: "POST",
            url: '/del_territories',
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

        if ( !proverka() ) return;

        let params = {
          name: $("#name-" + id[1]).val(),
          xStart: $("#xStart-" + id[1]).val(),
          zStart: $("#zStart-" + id[1]).val(),
          xStop: $("#xStop-" + id[1]).val(),
          zStop: $("#zStop-" + id[1]).val(),
          world: $("#world-" + id[1]).val(),
          edit: 1,
          markerID: id[1]
        };
  
        queryADD(params);
    });

    function proverka() {
      if (confirm("Подтвердить")) {
          return true;
      } else {
          return false;
      }
    }; 
  });