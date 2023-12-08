const sc = {
    service:{}
};

sc.service.request = function(endpoint,method,data={},callback=()=>{}) {
    const contentType = 'application/json';
    $.ajax({
        url:endpoint,
        method:method,
        contentType:contentType,
        data:JSON.stringify(data),
    }).done(
        (data) => {callback(data)}
    ).fail(
        (err) => {alert(err)}
    )

}