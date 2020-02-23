$(function(){
    console.log("loaded");

    // Format the time
    $('td.td.date').each(function() {
        $(this).html(moment($(this).html()*1000).format("YYYY/MM/DD HH:mm:ss"))
    });

    // Process the DataTable
    $('table#main_table').DataTable({
        paging: false,
        order: [0, "desc"]
    });

});