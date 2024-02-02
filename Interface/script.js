const sdAdmin = {}

sdAdmin.togglePage = function(abc) {
    const btn = $(abc);
    const tabName = btn.data('tab');
    const tab = $(`div#${tabName}`)

    btn.prop('disabled', true); // disable the clicked button
    btn.addClass('selectedButton');
    btn.siblings().prop('disabled', false); // enable all sibling buttons
    btn.siblings().removeClass('selectedButton');

    $('.tab').css({'display':'none'})
    tab.css({'display':'inline'})

    if (tabName == 'logs') {
        sc.server.listLogs();
    }
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

    // Append the table to div#logContents
    const tableContainer = $('div#logContents');
    tableContainer.children().remove();
    tableContainer.append(table);
}

$(document).ready(() => {
    let initialPage = 'firewallRules';

    let btn = $(`button[data-tab="${initialPage}"]`);
    let tab = $(`div#${initialPage}`);

    btn.prop('disabled',true)
    btn.addClass('selectedButton')

    $('.tab').css({'display':'none'})
    tab.css({'display':'inline'})
});