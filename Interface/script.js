if (typeof sdAdmin === 'undefined') { sdAdmin = {} };

sdAdmin.addEventHandlers = function() {
    const events = [
        {
            selector: 'button#firewallRefreshBtn',
            event:    'click',
            function: function(){sdAdmin.firewallMgr.refreshFirewallRules(true)}
        },
        {
            selector: 'button#firewallCommitBtn',
            event:    'click',
            function: sdAdmin.firewallMgr.commitFirewallRules
        },
        {
            selector: 'button#sftpUserRefreshBtn',
            event:    'click',
            function: sdAdmin.sftpUserMgr.listSftpUsers
        },
        {
            selector: 'button#sftpUserCreateBtn',
            event:    'click',
            function: sdAdmin.sftpUserMgr.createNewUserModal
        },
        {
            selector: 'button#loadLogBtn',
            event:    'click',
            function: sdAdmin.logger.loadLog
        },
        {
            selector: 'button#newRuleBtn',
            event:    'click',
            function: sc.service.DOMHandlers.addNewRule
        },
        {
            selector: 'button.tabToggleBtn',
            event:    'click',
            function: sdAdmin.togglePage
        }        
    ];
    events.forEach((evt) => {
        $(evt.selector).on(evt.event, evt.function);
    });  
}

sdAdmin.togglePage = function() {
    const btn = $(this);
    const tabName = btn.data('tab');
    const tab = $(`div#${tabName}`)

    btn.prop('disabled', true); // disable the clicked button
    btn.addClass('selectedButton');
    btn.siblings().prop('disabled', false); // enable all sibling buttons
    btn.siblings().removeClass('selectedButton');

    $('.tab').css({'display':'none'})
    tab.css({'display':'inline'})

    if (tabName == 'logs') {
        sdAdmin.logger.listLogs();
    } else if (tabName == 'sftpUserManagement') {}
}

sdAdmin.createTableFromData = function(data, columnOrder) {
    // Create a new table
    let table = $('<table></table>');

    // Create table header
    let thead = $('<thead></thead>');
    let headerRow = $('<tr></tr>');

    if (!columnOrder) { columnOrder = []; }

    // If columnOrder is provided, iterate over it to create headers
    for (let i = 0; i < columnOrder.length; i++) {
        headerRow.append(`<th>${columnOrder[i]}</th>`);
    }
    // Add remaining keys as headers
    for (let key in data[0]) {
        if (!columnOrder.includes(key)) {
            headerRow.append(`<th>${key}</th>`);
        }
    }

    thead.append(headerRow);
    table.append(thead);

    // Create table body
    let tbody = $('<tbody></tbody>');
    for (let i = 0; i < data.length; i++) {
        let row = $('<tr></tr>');
        if (i % 2 == 0) {
            row.addClass('logRowEven');
        } else {
            row.addClass('logRowOdd');
        }

        // If columnOrder is provided, iterate over it to create cells
        for (let j = 0; j < columnOrder.length; j++) {
            row.append(`<td>${data[i][columnOrder[j]]}</td>`);
        }
        // Add remaining keys as cells
        for (let key in data[i]) {
            if (!columnOrder.includes(key)) {
                row.append(`<td>${data[i][key]}</td>`);
            }
        }
        tbody.append(row);
    }
    table.append(tbody);

    return table;
}

sdAdmin.server = {
    checkVersion: function() {
        const contentType = 'application/json';
        $.ajax({
            url:'/checkVersion',
            method:'GET',
            contentType:contentType,
        }).done((data) => {
            if (!data) {
                $('div#timeToUpdate').css('display','block');
            }
        })
    }
}

$(document).ready(() => {
    window.notifications = new Notifications();
    let initialPage = 'firewallRules';

    let btn = $(`button[data-tab="${initialPage}"]`);
    let tab = $(`div#${initialPage}`);

    btn.prop('disabled',true)
    btn.addClass('selectedButton')

    $('.tab').css({'display':'none'})
    tab.css({'display':'inline'})

    sdAdmin.server.checkVersion();

    sdAdmin.firewallMgr.refreshFirewallRules();

    sdAdmin.addEventHandlers();

    setInterval(sdAdmin.firewallMgr.testFirewallChecksum,60000); // once per minute
});