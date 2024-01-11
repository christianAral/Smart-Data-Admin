const notifications = {};

notifications.card = $(
    '<div class="notification"><div class="notifHeader"><span class="notifTitle"></span><div class="notifHeaderRight"><span class="notifTime"></span><span class="notifClose" onclick="notifications.removeCard(this)">X</span></div></div><span class="notifBody"></span></div>'
);


$("body").append(
    $(
        '<div id="notifications"><div id="notifClearAll" onclick="notifications.clearNotifications()">Clear All Notifications</div></div>'
    )
);
notifications.notificationsContainer = $("div#notifications").first();

notifications.addCard = function(title, description, type) {
    let newCard = notifications.card.clone(true);

    if (["Error", "Warning"].includes(type)) {
        newCard.addClass(`notifStatus${type}`);
    } else {
        newCard.addClass("notifStatusInfo");
    }
    newCard.find(".notifTitle").text(title);
    newCard.find(".notifTime").text(formatDate());
    newCard.find(".notifBody").text(description);

    notifications.notificationsContainer.append(newCard);
}

notifications.removeCard = function(evt) {
    $(evt).closest(".notification").remove();
}

notifications.clearNotifications = function() {
    $('#notifications>.notification').remove()
}

function formatDate(date) {
    if (date === undefined) {
        date = new Date();
    }
    var hours = date.getHours();
    var minutes = date.getMinutes().toString().padStart(2, "0");
    var seconds = date.getSeconds().toString().padStart(2, "0");
    var ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    var strTime = hours + ":" + minutes + ":" + seconds + " " + ampm;
    return (
        date.getFullYear() +
        "-" +
        (date.getMonth() + 1).toString().padStart(2, "0") +
        "-" +
        date.getDate().toString().padStart(2, "0") +
        " " +
        strTime
    );
}
