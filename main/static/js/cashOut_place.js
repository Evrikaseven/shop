var items = $('.item'),
    cashOut = $('#cash-out'),
    sum = 0;

$.each(items, function (value) {
    var itemVal = parseFloat(items[value].innerHTML);
    sum += !isNaN(itemVal)?itemVal:0;
});

cashOut.html('Total: ' + sum + ' ₽');

