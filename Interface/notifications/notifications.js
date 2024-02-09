const notifications = {
    templates:{},
    helperFn:{
        generateID: function(N) {
            var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
            var result = '';
            for (var i = 0; i < N; i++) {
                result += characters.charAt(Math.floor(Math.random() * characters.length));
            }
            return result;
        },
        formatDate: function () {
            const date = new Date();
            const year = date.getFullYear();
            const month = (date.getMonth() + 1).toString().padStart(2, "0");
            const day = date.getDate().toString().padStart(2, "0");
            const timeString = date.toLocaleTimeString('en-US', { hour12: true, hour: '2-digit', minute: '2-digit', second: '2-digit' });
            return `${year}-${month}-${day} ${timeString}`;
        }
    }
};

notifications.id=`n${notifications.helperFn.generateID(8)}`;

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

notifications.container = $(
    `<div id="${notifications.id}" class="notifications"><div id="notifClearAll">Clear All Notifications</div></div>`
)

notifications.container.find('#notifClearAll').click(function() {
    $(`#${notifications.id}>.notification`).remove()
})

$("body").append(notifications.container);

notifications.addCard = function(title, description, type) {
    let newCard = notifications.templates.card.clone(true);

    if (["Error", "Warning"].includes(type)) {
        newCard.addClass(`notifStatus${type}`);
    } else {
        newCard.addClass("notifStatusInfo");
    }
    newCard.find(".notifTitle").text(title);
    newCard.find(".notifBody").text(description);
    newCard.find(".notifTime").text(notifications.helperFn.formatDate());

    notifications.container.append(newCard);
}
