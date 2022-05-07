$( document ).ready(function() {
    $( "#add" ).click( function() {
      let params = {
        name_category: $("#name-add").val(),
        action: "add"
      };

      if ( !proverka() ) return;

      queryADD(params);
    });

    function queryADD (params) {
      $.ajax({
        type: "POST",
        url: '/category',
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
            cell1 = row.insertCell(0).outerHTML = '<th><input type="text" placeholder="' + params.name_category + '" name="name" id="name-' + res.success + '" value="' + params.name_category + '"></th>';
            cell2 = row.insertCell(1).outerHTML = '<th><button id="edit-' + res.success + '">Изменить</button></th>';
            cell3 = row.insertCell(2).outerHTML = '<th><button id="del-' + res.success + '">Удалить</button></th>';

            row.setAttribute("id", "tr-" + res.success);
          }

          $(document).on("click" , "#del-" + res.success , function() {
            let params = {
                id: res.success,
                action: 'delete'
            };
        
            queryDEL(params)

            $(this).parent().parent().remove();
          } );

          $(document).on("click" , "#edit-" + res.success , function() {
            let paramsUpdate = {
                name_category: $("#name-" + res.success).val(),
                action: 'edit',
                id: res.success
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
          id: id[1],
          action: 'delete'
        };
        
        if ( !proverka() ) return;

        queryDEL(params);
    });

    function queryDEL (params) {
        $.ajax({
            type: "POST",
            url: '/category',
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
          name_category: $("#name-" + id[1]).val(),
          action: 'edit',
          id: id[1]
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