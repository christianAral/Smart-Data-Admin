const sc = {
    service:{
        DOMHandlers:{},
        events:{}
    },
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

sc.service.DOMHandlers.createTableRow = function(ipName,ipStart,ipEnd) {
    const uuid = crypto.randomUUID();
    let tds = [
        `<td><input class='ruleData' onfocusout='sc.service.events.ruleUpdated(this)' value='${ipName}' data-orig='${ipName}'></td>`,
        `<td><input class='ruleData' onfocusout='sc.service.events.ruleUpdated(this)' value='${ipStart}' data-orig='${ipStart}'</td>`,
        `<td><input class='ruleData' onfocusout='sc.service.events.ruleUpdated(this)' value='${ipEnd}' data-orig='${ipEnd}'</td>`
    ];
    const tr = `<tr>${tds.join('')}</tr>`

    return tr
}

sc.service.events.ruleUpdated = function(evt) {
    const tr = $(evt).parent().parent();

    if (evt.dataset.orig == evt.value) {
        tr.removeClass('changedRow');        
    } else {
        tr.addClass('changedRow');
    }
}

sc.server.refreshFirewallRules = function() {
    const contentType = 'application/json';
    $.ajax({
        url:'/refreshFirewallRules',
        method:'GET',
        contentType:contentType,
    }).done((data) => {
        const currRulesBody = $('table#currentRules>tbody');
        bodyContent = data.map((e) => { return sc.service.DOMHandlers.createTableRow(e.name,e.start,e.end); })
            .sort((a,b) => a.localeCompare(b)).join('');

        currRulesBody.html(bodyContent)
    });
}