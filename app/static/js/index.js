let socket = io();

function actionLink(index, action, text) {
    var ret = `<a href="javascript:void(0)" onclick="sendAction(${index}, ${action})">${text}</a>`;
    return ret;
}

function sendAction(index, action) {
    socket.emit("queue_action", {"index": index, "action": action});
}

$(function() {
    let refreshTime = $("#refreshTime");
    let info = $("#info");

    let consoleTopBox = $("#scroller");
    let rconconsole = $("#consoleBox");
    let aicmd = $("#aicmd");
    let rconcmd = $("#rconcmd");
    let sendaicmd = $("#sendaicmd");
    let sendrconcmd = $("#sendrconcmd");
    
    let killswitch = $("#killSwitch");
    let autoDisableVoice = $("#autoDisableVoice");
    
    let scrolls = 0;

    function sendCmd(event) {
        var type = event.data.type;
        var message = event.data.message.val();
        console.log(event.data);
        if (message.trim() == "") {
            info.innerHTML = "Empty message.";
            return;
        }
        
        socket.emit("send_cmd", {
            "type": type,
            "message": message,
        });
        
        info.innerHTML = "Sent message.";
    }   
    function enterCmd(event) {
        if (event.which != 13) {
            return;
        }
        event.preventDefault();
        if (event.data.type == "ai") {
            sendaicmd.trigger("click");
        } else {
            sendrconcmd.trigger("click");
        }
    }

    function killSwitchChanged() {
        socket.emit("set_killswitch", killswitch.is(":checked"));
    }

    function autoDisableVoiceChanged() {
        socket.emit("set_auto_disable_voice", autoDisableVoice.is(":checked"));
    }
        
    aicmd.on("keydown",     {"type": "ai", "message": aicmd},       enterCmd);
    rconcmd.on("keydown",   {"type": "rcon", "message": rconcmd},   enterCmd);
    sendaicmd.on("click",   {"type": "ai", "message": aicmd},       sendCmd);
    sendrconcmd.on("click", {"type": "rcon", "message": rconcmd},   sendCmd);
    killswitch.on("click", killSwitchChanged);
    autoDisableVoice.on("click", autoDisableVoiceChanged);

    socket.on("consoleget", (data) => {
        rconconsole.html(data);
        if (scrolls == 0) consoleTopBox.scrollTop(consoleTopBox[0].scrollHeight - consoleTopBox[0].clientHeight);
        scrolls++;
    });

    socket.on("queueget", (queue) => {
        $("#queuelength").text(queue.length);
        $("#queue tbody").empty();
        var markup = "";
        if (queue.length >= 1) {
            for (var i = 0; i < queue.length; i++) {
                var actionHTML = `${actionLink(i, 0, "del")} ` +
                `Send ${actionLink(i, 1, "up")}/${actionLink(i, 2, "down")} in queue. ` +
                `Send to ${actionLink(i, 3, "front")}/${actionLink(i, 4, "back")}`;
                var elem = queue[i];
                markup += `<tr><td>${elem['username']}</td><td>${elem['message']}</td><td>${actionHTML}</td></tr>`;
            }
        } else {
            markup = "<tr><td colspan=\"3\">the queue is empty</td></tr>"
        }
        $("#queue tbody").append(markup);
    });

    killSwitchChanged();
    autoDisableVoiceChanged();
});