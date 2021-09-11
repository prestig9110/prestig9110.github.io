$(document).ready(function() {
  $.fn.dataTable.ext.errMode = 'none';
  var t = $('#example').DataTable( {
    "ajax": "/getStats",
    "columns": [
        { "data": null, "className": "dt-head-left" },
        { "data": "name", "className": "dt-head-left" },
        { "data": "active_playtime", "render": dhm, "orderData": 8 , "className": "dt-head-left" },
        { "data": "afk", "render": dhm, "orderData": 9 , "className": "dt-head-left" },
        { "data": "deaths" , "className": "dt-head-left" },
        { "data": "mobs" , "className": "dt-head-left" },
        { "data": "broken" , "className": "dt-head-left" },
        { "data": "supplied" , "className": "dt-head-left" },
        { "data": "active_playtime", "className": "dt-head-left", "visible": false },
        { "data": "afk", "className": "dt-head-left", "visible": false }
    ],
    order: [[ 8, 'desc' ]],
    pageLength : 15,
    "bLengthChange": false,
    "bInfo": false,
    "language": {
      "url": "https://cdn.datatables.net/plug-ins/1.11.1/i18n/ru.json"
    }
  } );
  t.on( 'order.dt search.dt', function () {
    t.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
      cell.innerHTML = i+1;
    } );
  } ).draw();
} );

function dhm(t){
  var cd = 24 * 60 * 60 * 1000,
    ch = 60 * 60 * 1000,
    d = Math.floor(t / cd),
    h = Math.floor((t - d * cd) / ch),
    m = Math.round((t - d * cd - h * ch) / 60000),
    pad = function(n){ return n < 10 ? '0' + n : n; };
  if( m === 60 ){
    h++;
    m = 0;
  }
  if( h === 24 ){
    d++;
    h = 0;
  }

  if (d == 0 && h > 0) {
    return pad(h) + "ч " + pad(m) + "м";
  } 

  if (d == 0 && h == 0 && m > 0) {
    return pad(m) + "м";
  }

  if (d == 0 && h == 0 && m == 0) {
    return "< 00м";
  }

  return d + "д " + pad(h) + "ч " + pad(m) + "м";
}