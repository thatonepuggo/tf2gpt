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
    
    let lastQueue = [];
    let lastConsole = "";

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

    function arrayCompare(_arr1, _arr2) {
        if (
          !Array.isArray(_arr1)
          || !Array.isArray(_arr2)
          || _arr1.length !== _arr2.length
          ) {
            return false;
          }
        
        // .concat() to not mutate arguments
        const arr1 = _arr1.concat().sort();
        const arr2 = _arr2.concat().sort();
        
        for (let i = 0; i < arr1.length; i++) {
            if (arr1[i] !== arr2[i]) {
                return false;
             }
        }
        
        return true;
    }
        
    aicmd.on("keydown",     {"type": "ai", "message": aicmd},       enterCmd);
    rconcmd.on("keydown",   {"type": "rcon", "message": rconcmd},   enterCmd);
    sendaicmd.on("click",   {"type": "ai", "message": aicmd},       sendCmd);
    sendrconcmd.on("click", {"type": "rcon", "message": rconcmd},   sendCmd);
    killswitch.on("click", killSwitchChanged);
    autoDisableVoice.on("click", autoDisableVoiceChanged);

    socket.on("consoleget", (data) => {
        if (lastConsole == data) return;
        rconconsole.html(data);
        lastConsole = data;
        if (scrolls == 0) consoleTopBox.scrollTop(consoleTopBox[0].scrollHeight - consoleTopBox[0].clientHeight);
        scrolls++;
    });

    socket.on("queueget", (queue) => {
        if (arrayCompare(lastQueue, queue)) return;
        
        $("#queuelength").text(queue.length);
        $("#queue tbody").empty();
        
        var markup = "";        
        
        for (var i = 0; i < queue.length; i++) {
            var actionHTML = `${actionLink(i, 0, "del")} ` +
            `Send ${actionLink(i, 1, "up")}/${actionLink(i, 2, "down")} in queue. ` +
            `Send to ${actionLink(i, 3, "front")}/${actionLink(i, 4, "back")}`;
            var elem = queue[i];
            markup += `<tr><td>${elem['username']}</td><td>${elem['message']}</td><td>${actionHTML}</td></tr>`;
        }

        lastQueue = queue;

        $("#queue tbody").append(markup);
    });

    killSwitchChanged();
    autoDisableVoiceChanged();
});