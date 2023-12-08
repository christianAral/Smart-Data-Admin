const sc = {
    service:{},
    server:{}
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
        (err) => {alert(JSON.stringify(err))}
    )

}

sc.server.refreshFirewallRules = function() {
    const contentType = 'application/json';
    $.ajax({
        url:'/refreshFirewallRules',
        method:'GET',
        contentType:contentType,
    }).done((data) => {
        const currRulesBody = $('table#currentRules>tbody');
        bodyContent = data.map((e) => { return `<tr><td>${e.name}</td><td>${e.start}</td><td>${e.end}</td></tr>` })
            .sort((a,b) => a.localeCompare(b)).join('');

        currRulesBody.html(bodyContent)
    });
}