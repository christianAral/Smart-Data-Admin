if (typeof sdAdmin === 'undefined') { sdAdmin = {} };

sdAdmin.sftpUserMgr = {};

sdAdmin.sftpUserMgr.listSftpUsers = function(notify) {
    $('*').css('cursor','wait')
    $('button#sftpUserRefreshBtn').prop('disabled', true);
    const contentType = 'application/json';
    $.ajax({
        url:'/sftpmgr',
        method:'GET',
        contentType:contentType,
    }).done((data) => {
        sc.tempdata = data;
        sdAdmin.sftpUserMgr.createTable(data,'div#sftpUsers');

        if (notify) {
            notifications.addCard('SFTP User List Refreshed','','Info');
        }
    }).always(() => {
        $('*').css('cursor','')
        $('button#sftpUserRefreshBtn').prop('disabled', false);
    });
};

sdAdmin.sftpUserMgr.createTable = function (data, tableContainer) {
    const container = $(tableContainer);
    container.children().remove();

    const table = $(
        "<table><tr><th>Name</th><th>HomeDirectory</th></tr></table>"
    );

    data.sort(function (a, b) {
        var nameA = a.Name.toUpperCase(); // ignore upper and lowercase
        var nameB = b.Name.toUpperCase(); // ignore upper and lowercase
        if (nameA < nameB) {
            return -1;
        }
        if (nameA > nameB) {
            return 1;
        }

        // names must be equal
        return 0;
    });

    for (let i = 0; i < data.length; i++) {
        let r = data[i];
        const row = $(`<tr id='${btoa(r.ARN)}'>
                         <td>${r.Name}</td>
                         <td>${r.HomeDirectory}</td>
                         <td><button onclick="sdAdmin.sftpUserMgr.retrievePassword('${btoa(r.ARN)}')">
                           Retrieve Password</button></td>
                         </tr>`);

        if (i % 2 == 0) {
            row.addClass("logRowEven");
        } else {
            row.addClass("logRowOdd");
        }

        table.append(row);
    }
    container.append(table);
};

sdAdmin.sftpUserMgr.retrievePassword = function (ARN_b64) {
    $('*').css('cursor','wait')
    // $('button#firewallCommitBtn').prop('disabled', true);
    const contentType = 'application/json';

    const passphrase = window.prompt('Enter a passphrase here if you want retrieving the secret to require a passphrase or leave blank for none');
    const payload = {"ARN_b64":ARN_b64,"passphrase":passphrase};

    $.ajax({
        url:'/sftpmgr/secret',
        method:'POST',
        contentType:contentType,
        data:JSON.stringify(payload)
    }).done((data) => {
        notifications.addCard('Retrieved Password Available',data.secret_url,'Info');
    }).always(() => {
        $('*').css('cursor','')
        // $('button#firewallCommitBtn').prop('disabled', false);
    });
}
