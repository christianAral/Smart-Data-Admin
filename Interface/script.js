const sdAdmin = {}

sdAdmin.togglePage = function(abc) {
    let btn = $(abc);
    btn.prop('disabled', true); // disable the clicked button
    btn.addClass('selectedButton');
    btn.siblings().prop('disabled', false); // enable all sibling buttons
    btn.siblings().removeClass('selectedButton');

    let tabName = btn.data('tab');

    let tab = $(`div#${tabName}`)
    $('.tab').css({'display':'none'})
    tab.css({'display':'inline'})
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