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

};

sc.service.isValidIPV4 = function(input) {
    var ipv4Pattern = /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipv4Pattern.test(input);
}

sc.service.DOMHandlers.createTableRow = function(ipName,ipStart,ipEnd) {
    const uuid = crypto.randomUUID();
    let tds = [
        `<td><input class='ruleData ruleName' onfocusout='sc.service.events.inputLoseFocus(this)' value='${ipName}' data-orig='${ipName}' /></td>`,
        `<td><input class='ruleData' onfocusin='sc.service.events.inputGainFocus(this,"ip")' onfocusout='sc.service.events.inputLoseFocus(this,"ip")' value='${ipStart}' data-orig='${ipStart}'/></td>`,
        `<td><input class='ruleData' onfocusin='sc.service.events.inputGainFocus(this,"ip")' onfocusout='sc.service.events.inputLoseFocus(this,"ip")' value='${ipEnd}' data-orig='${ipEnd}'/></td>`,
        `<td><button class='resetBtn' onclick="sc.service.DOMHandlers.resetRow(this)" disabled>Reset</button></td>`,
        `<td><button class='deleteBtn' onclick="sc.service.DOMHandlers.toggleDelete(this)">Toggle Delete</button></td>`
    ];
    const tr = `<tr>${tds.join('')}</tr>`

    return tr
};

sc.service.DOMHandlers.resetRow = function(evt) {
    const tr = $(evt).closest('tr');
    const inputs = tr.find('input');
  
    inputs.each(function() {
        $(this).val($(this).data('orig'));
    });

    sc.service.DOMHandlers.updateRowState(tr);
};

sc.service.DOMHandlers.toggleDelete = function(evt) {
    const tr = $(evt).closest('tr');
  
    if (tr.data('state') != 'deletedRow') {
        sc.service.DOMHandlers.updateRowState(tr,'deletedRow');
    } else {
        sc.service.DOMHandlers.updateRowState(tr);
    }

};

sc.service.DOMHandlers.checkRowChangedState = function(tr) {
    const inputs = tr.find('input');

    let allMatch = true;

    inputs.each(function() {
        if ($(this).val() !== $(this).data('orig')) {
            allMatch = false;
            return false;
        } 
    });

    if (allMatch) {
        sc.service.DOMHandlers.updateRowState(tr);
    } else {
        sc.service.DOMHandlers.updateRowState(tr,'changedRow');
    }
};

sc.service.DOMHandlers.inputGainFocus = function(inp,type) {
    const input = $(inp);

    if (type == 'ip') {
        input.data('latest',input.val());
    }
}

sc.service.DOMHandlers.inputLoseFocus = function(inp,type) {
    const input = $(inp);
    const tr = tr.closest('tr');

    if (type == 'ip') {
        if (!sc.service.isValidIPV4(input.val())) {
            alert("That's not a valid IPV4, must be in format 111.222.333.444!");
            input.val(input.data('latest'));
            return false;
        }
    }

    sc.service.DOMHandlers.checkRowChangedState(tr);
}

sc.service.DOMHandlers.updateRowState = (tr, state) => {
    const states = ['changedRow', 'deletedRow', 'addedRow'];
    const inputs = tr.find('input');
    const button = tr.find('button.resetBtn');

    states.forEach((s) => tr.removeClass(s));

    if (state == 'changedRow') {
        // enable reset button
        tr.data('state',state);
        tr.addClass(state);
        button.prop('disabled',false);
    } else if (state == 'deletedRow') { 
        // disable inputs and enable reset button
        tr.data('state',state);
        tr.addClass(state);
        inputs.each(function() { $(this).prop('disabled',true); });
        button.prop('disabled',false);
    } else if (state == 'addedRow') {
        tr.data('state',state);
        tr.addClass(state);

    } else { 
        // enable inputs and disable the reset button 
        tr.removeData('state');
        inputs.each(function() { $(this).prop('disabled',false); });
        button.prop('disabled',true);
    }
};

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
};

sc.server.commitFirewallRules = function() {
    alert("This is where there'll be code to update the firewall rules");
};


$(document).ready(() => {
    sc.server.refreshFirewallRules();
});