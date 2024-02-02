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
    return ipv4Pattern.test(input) || input == '' || input === undefined;
}

sc.service.isValidRuleName = function() {
    var ruleNames = $('input.ruleName').map(function() {
        return $(this).val();
    }).get();
    
    var uniqueRuleNames = new Set(ruleNames);
    
    return (uniqueRuleNames.size === ruleNames.length)
}

sc.service.DOMHandlers.createTableRow = function(ipName,ipStart,ipEnd,isNewRow=false) {
    const uuid = crypto.randomUUID();

    const buttonSetExisting = [
        `<td><button class='resetBtn' onclick="sc.service.DOMHandlers.resetRow(this)" disabled>Reset</button>`,
        `<button class='deleteBtn' onclick="sc.service.DOMHandlers.toggleDelete(this)">Toggle Delete</button></td>`
    ];

    const buttonSetNew = [
        `<td><button class='removeBtn' onclick="sc.service.DOMHandlers.removeRow(this)">Remove Row</button></td>`
    ];

    let tds = [
        `<td><input class='ruleData ruleName'  onfocusin='sc.service.events.inputGainFocus(this)' onfocusout='sc.service.events.inputLoseFocus(this,"name")' value='${ipName}'  data-orig='${ipName}' /></td>`,
        `<td><input class='ruleData ruleStart' onfocusin='sc.service.events.inputGainFocus(this)' onfocusout='sc.service.events.inputLoseFocus(this,"ip")'   value='${ipStart}' data-orig='${ipStart}'/></td>`,
        `<td><input class='ruleData ruleEnd'   onfocusin='sc.service.events.inputGainFocus(this)' onfocusout='sc.service.events.inputLoseFocus(this,"ip")'   value='${ipEnd}'   data-orig='${ipEnd}'  /></td>`
    ];

    if (isNewRow) { tds.push(...buttonSetNew)      }
    else          { tds.push(...buttonSetExisting) }
    const tr = `<tr>${tds.join('')}</tr>`

    return tr
};

sc.service.DOMHandlers.addNewRule = function() {
    const tbody = $('table#currentRules').find('tbody');
    const tr = $(sc.service.DOMHandlers.createTableRow('','','',true));

    sc.service.DOMHandlers.updateRowState(tr,'addedRow')
    tbody.prepend(tr);
}

sc.service.DOMHandlers.resetRow = function(evt) {
    const tr = $(evt).closest('tr');
    const inputs = tr.find('input');
  
    inputs.each(function() {
        $(this).val($(this).data('orig'));
    });

    sc.service.DOMHandlers.updateRowState(tr);
};

sc.service.DOMHandlers.removeRow = function(evt) {
    const tr = $(evt).closest('tr');
    tr.remove();
}

sc.service.DOMHandlers.toggleDelete = function(evt) {
    const tr = $(evt).closest('tr');
  
    if (!tr.hasClass('deletedRow')) {
        sc.service.DOMHandlers.updateRowState(tr,'deletedRow');
    } else {
        sc.service.DOMHandlers.checkRowChangedState(tr);
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

sc.service.events.inputGainFocus = function(inp) {
    const input = $(inp);
    input.data('latest',input.val());
}

sc.service.events.inputLoseFocus = function(inp,type) {
    const input = $(inp);
    const tr = input.closest('tr');

    if (type == 'ip') {
        if (!sc.service.isValidIPV4(input.val())) {
            alert("That's not a valid IPV4, must be in format 111.222.333.444!");
            input.val(input.data('latest'));
            return false;
        }
    } else if (type == 'name') {
        if (!sc.service.isValidRuleName()) {
            alert("It looks like that rule name is already in use! Please use something else.");
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

    // don't do anything else if the state is already set as addedRow
    if (tr.hasClass('addedRow')) { return true }

    states.forEach((s) => tr.removeClass(s));

    if (state == 'changedRow') {
        // enable reset button
        tr.addClass(state);
        button.prop('disabled',false);
    } else if (state == 'deletedRow') { 
        // disable inputs and enable reset button
        tr.addClass(state);
        inputs.each(function() { $(this).prop('disabled',true); });
        button.prop('disabled',false);
    } else if (state == 'addedRow') {
        tr.addClass(state);

    } else { 
        // enable inputs and disable the reset button 
        inputs.each(function() { $(this).prop('disabled',false); });
        button.prop('disabled',true);
    }
};

sc.server.listSftpUsers = function(notify) {
    $('*').css('cursor','wait')
    $('button#sftpUserRefresh').prop('disabled', true);
    const contentType = 'application/json';
    $.ajax({
        url:'/sftpmgr',
        method:'GET',
        contentType:contentType,
    }).done((data) => {
        sc.tempdata = data;
        const table = sdAdmin.createTableFromData(data,['Name','HomeDirectory']);
        const tableContainer = $('div#sftpUsers');
        tableContainer.children().remove();
        tableContainer.append(table);

        if (notify) {
            notifications.addCard('SFTP User List Refreshed','','Info');
        }
    }).always(() => {
        $('*').css('cursor','')
        $('button#sftpUserRefresh').prop('disabled', false);
    });
};

// sc.server.getSftpUser = function(notify) {
//     $('*').css('cursor','wait')
//     const contentType = 'application/json';
//     const ARN_b64 = btoa('This is where the selected ARN will go');
//     $.ajax({
//         url:`/sftpmgr/${ARN_b64}`,
//         method:'GET',
//         contentType:contentType,
//     }).done((data) => {
//         console.log(data);

//         if (notify) {
//             notifications.addCard('SFTP User Was Retrieved','','Info');
//         }
//     }).always(() => {
//         $('*').css('cursor','')
//     });
// };

$(document).ready(() => {
    sdAdmin.firewallMgr.refreshFirewallRules();
});