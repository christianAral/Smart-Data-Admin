if (typeof sdAdmin === 'undefined') { sdAdmin = {} };

sdAdmin.logger = {};

sdAdmin.logger.listLogs = function(notify) {
    $('*').css('cursor','wait')
    const contentType = 'application/json';
    $.ajax({
        url:'/logs',
        method:'GET',
        contentType:contentType,
    }).done((data) => {
        const logSelect = $('select#logFiles');
        logSelect.children().remove()
        data.sort().reverse()
        data.forEach((d) => {
            let opt = $('<option>');
            opt.val(atob(d));
            opt.text(atob(d));
            logSelect.append(opt);
        });

        if (notify) {
            notifications.addCard('Log List Updated','','Info');
        }
    }).always(() => {
        $('*').css('cursor','')
    });
};

sdAdmin.logger.loadLog = function(notify) {
    $('*').css('cursor','wait')
    const contentType = 'application/json';
    const logFile = btoa($('select#logFiles').val())
    $.ajax({
        url:`/logs/${logFile}`,
        method:'GET',
        contentType:contentType,
    }).done((data) => {
        const table = sdAdmin.createTableFromData(data,['timestamp','type','user','message']);
        const tableContainer = $('div#logContents');
        tableContainer.children().remove();
        tableContainer.append(table);

        if (notify) {
            notifications.addCard('Log Loaded','','Info');
        }
    }).always(() => {
        $('*').css('cursor','')
    });
};