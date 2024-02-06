if (typeof sdAdmin === 'undefined') { sdAdmin = {} };

sdAdmin.firewallMgr = {};

sdAdmin.firewallMgr.testFirewallChecksum = function() {
    if (sdAdmin.firewallMgr.status == 'synced') {
        const contentType = 'application/json';
        $.ajax({
            url:'/testFirewallChecksum',
            method:'GET',
            contentType:contentType,
        }).done((data) => {
            if (!data.synced) {
                sdAdmin.firewallMgr.status = 'not synced';
                notifications.addCard('Local Firewall Rules are out of sync!','Click "Refresh Firewall Rules" to pull the latest rules from the server.','Error');
            }
        });
    }
}

sdAdmin.firewallMgr.refreshFirewallRules = function(notify) {
    $('*').css('cursor','wait')
    $('button#firewallRefreshBtn').prop('disabled', true);
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

        sdAdmin.firewallMgr.status = 'synced';

        if (notify) {
            notifications.addCard('Firewall Rules Refreshed','','Info');
        }
    }).always(() => {
        $('*').css('cursor','')
        $('button#firewallRefreshBtn').prop('disabled', false);
    });
};

sdAdmin.firewallMgr.commitFirewallRules = function() {
    $('*').css('cursor','wait')
    $('button#firewallCommitBtn').prop('disabled', true);
    const states = ['changedRow', 'deletedRow', 'addedRow'];
    const contentType = 'application/json';
    const payload = {};

    states.forEach((s) => {
        payload[s] = $(`tbody>tr.${s}`).map(function(){
            const tr = $(this);
            const keys = {};
            
            keys.key = tr.find('input.ruleName').data('orig');
            keys.name = tr.find('input.ruleName').val();
            keys.start = tr.find('input.ruleStart').val();
            keys.end = tr.find('input.ruleEnd').val();
            
            return keys
        }).get()
    });

    $.ajax({
        url:'/updateFirewallRules',
        method:'POST',
        contentType:contentType,
        data:JSON.stringify(payload)
    }).done((data) => {
        if (JSON.stringify(data.instructions) == JSON.stringify(data.success)) {
            notifications.addCard('Firewall Rules Committed',JSON.stringify(data.instructions),'Warning');
        } else {
            notifications.addCard('Firewall Rules Committed',JSON.stringify((({ instructions, failure }) => ({ instructions, failure }))(data)),'Error');
        }

        sdAdmin.firewallMgr.refreshFirewallRules();
    }).always(() => {
        $('*').css('cursor','')
        $('button#firewallCommitBtn').prop('disabled', false);
    });
};