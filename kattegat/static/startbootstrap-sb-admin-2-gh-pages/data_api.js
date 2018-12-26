function desc_table(params) {
    $.ajax({
        url: 'raw_desc_table?table=' + params.table,
        success: params.func
    });
}

function sys_perf_columns(params) {
    $.ajax({
        url: 'api_sys_perf_log_columns?cdlog_id=' + params.cdlog_id,
        success: params.func
    })
};
