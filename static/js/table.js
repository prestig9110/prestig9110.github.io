$(document).ready(function() {
  $.fn.dataTable.ext.errMode = 'none';
    $('#example').DataTable( {
        "ajax": "/getStats",
        "columns": [
            { "data": "name" },
            { "data": "active_playtime", "render": dhm, "orderData": 6 },
            { "data": "deaths" },
            { "data": "mobs" },
            { "data": "broken" },
            { "data": "supplied" },
            { "data": "active_playtime", "visible": false }
        ],
        order: [[ 6, 'desc' ]],
        pageLength : 20,
        "bLengthChange": false,
        "bInfo": false,
        "language": {
          "url": "https://cdn.datatables.net/plug-ins/1.11.1/i18n/ru.json"
        }
    } );
} );

function dhm(t){
    var cd = 24 * 60 * 60 * 1000,
        ch = 60 * 60 * 1000,
        d = Math.floor(t / cd),
        h = Math.floor( (t - d * cd) / ch),
        m = Math.round( (t - d * cd - h * ch) / 60000),
        pad = function(n){ return n < 10 ? '0' + n : n; };
  if( m === 60 ){
    h++;
    m = 0;
  }
  if( h === 24 ){
    d++;
    h = 0;
  }
  return d + " д, " + pad(h) + " ч, " + pad(m) + " м";
}