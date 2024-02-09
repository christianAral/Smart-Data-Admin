const notifications = {
    templates:{},
    helperFn:{},
    id:`n${generateID(8)}`
};

notifications.templates.card = $(
    `<div class="notification">
         <div class="notifHeader">
             <span class="notifTitle"></span>
             <div class="notifHeaderRight">
                 <span class="notifTime"></span>
                 <span class="notifClose">X</span>
             </div>
         </div>
         <span class="notifBody"></span>
     </div>`
);

notifications.templates.card.find('.notifClose').click(function() {
    $(this).closest(".notification").remove();
})

notifications.templates.container = $(
    `<div id="${notifications.id}" class="notifications"><div id="notifClearAll">Clear All Notifications</div></div>`
)

notifications.templates.container.find('#notifClearAll').click(function() {
    $(`#${notifications.id}>.notification`).remove()
})

$("body").append(notifications.templates.container);

notifications.notificationsContainer = $(`div#${notifications.id}`).first();

notifications.addCard = function(title, description, type) {
    let newCard = notifications.templates.card.clone(true);

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

function generateID(N) {
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    var result = '';
    for (var i = 0; i < N; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return result;
}