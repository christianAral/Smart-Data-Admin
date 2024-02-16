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
        "<table><thead><tr><th>Name</th><th>HomeDirectory</th></tr></thead><tbody></tbody></table>"
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
                         <td class='sftp-name'>${r.Name.slice(5)}</td>
                         <td class='sftp-dir'>${r.HomeDirectory}</td>
                         <td><button onclick="sdAdmin.sftpUserMgr.retrievePassword('${btoa(r.ARN)}')">
                           Retrieve Password</button></td>
                         </tr>`);

        if (i % 2 == 0) {
            row.addClass("logRowEven");
        } else {
            row.addClass("logRowOdd");
        }

        table.find('tbody').append(row);
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
        notifications.addCard('Password Retrieved','OneTimeSecret.com Link','Info',data.secret_url);
    }).always(() => {
        $('*').css('cursor','')
        // $('button#firewallCommitBtn').prop('disabled', false);
    });
}

sdAdmin.sftpUserMgr.createNewUserModal = function () {

    // disable all other buttons
    $('button:not([disabled]):not(.modal button)')
        .addClass('disabledByModal')
        .prop('disabled',true);

    const dirs = [];
    $('.sftp-dir').each((i, n) => {
        if (!dirs.map((d) => d.toLowerCase()).includes(n.innerText.toLowerCase())) 
            dirs.push(n.innerText);
    });
    dirs.sort();

    const modal = $('<div id="sftpNewUSer">')
        .addClass('modal')
    const nameDiv = $('<div>').append($('<span>').text('Rule Name: '));
    const dirDiv = $('<div>').append($('<span>').text('Home Directory: '));
    const passDiv = $('<div>').append($('<span>').text('Password: '));
    const btnDiv = $('<div id="modalBtnDiv">');
    const nameInput = $('<input>').css('width','15em');
    const dirInput = $('<input list="existingSftpPathList">').css('width','15em');
    const datalist = $('<datalist id="existingSftpPathList">');
    const passInput = $('<input type="password">').css('width','13em');
    const randPassBtn = $('<button>')
        .text("!")
        .css('width','2em')
        .on('click',sdAdmin.sftpUserMgr.randPass);
    dirs.forEach((d) => {
        let opt = $('<option>').val(d);
        datalist.append(opt);
    })
    const submitErrorDiv = $('<div>').text('name or directory are missing!');

    const submitBtn = $('<button>')
        .text('Submit')
        .on('click',function(event) {
            if (nameInput.val() == '' || dirInput.val() == '') {
                submitErrorDiv.insertBefore(btnDiv);
            } else {
                let payload = {
                    username:`SFTP/${nameInput.val()}`,
                    password:passInput.val(),
                    homedir:dirInput.val()
                }


                $('*').css('cursor','wait')
                $('.modal button').prop('disabled', true);
                const contentType = 'application/json';
            
                $.ajax({
                    url:'/sftpmgr/create',
                    method:'POST',
                    contentType:contentType,
                    data:JSON.stringify(payload)
                }).done((data) => {
                    notifications.addCard('New SFTP User Created',data.Name,'Info');
                    sdAdmin.sftpUserMgr.modalCleanup(event);
                }).fail((data) => {
                    notifications.addCard('Something Went Wrong','Error creating SFTP user','error');
                }).always(() => {
                    $('*').css('cursor','')
                    $('.modal button').prop('disabled', false);
                });


            }
        })
    const cancelBtn = $('<button>')
        .text('Cancel')
        .on('click',sdAdmin.sftpUserMgr.modalCleanup);

    const modalParts = [
        nameDiv.append(nameInput),
        passDiv.append([randPassBtn,passInput]),
        dirDiv.append([dirInput,datalist]),
        btnDiv.append([submitBtn,cancelBtn])
    ];

    modal.append(modalParts);

    $('#sftpUserManagement').find('#sftpNewUSer').remove();
    $('#sftpUserManagement').append(modal);
    $('body').css('overflow','hidden');
}

sdAdmin.sftpUserMgr.modalCleanup = function(event) {
    $(event.target).closest('.modal').remove();
    $('body').css('overflow','');

    $('.disabledByModal')
        .prop('disabled',false)
        .removeClass('disabledByModal');

}


sdAdmin.sftpUserMgr.randPass = function(event) {
    // $('*').css('cursor','wait')
    // $('button#sftpUserRefreshBtn').prop('disabled', true);
    const contentType = 'application/json';
    $.ajax({
        url:'/sftpmgr/randpass',
        method:'GET',
        contentType:contentType,
    }).done((data) => {
        console.log(data)
        $(event.target).siblings('input').val(data.password);
    }).always(() => {
        // $('*').css('cursor','')
        // $('button#sftpUserRefreshBtn').prop('disabled', false);
    });
}