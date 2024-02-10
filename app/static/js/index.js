$(function() {
    var socket = io();

    let refreshTime = $("#refreshTime");
    let info = $("#info");

    let consoleTopBox = $("#consoleTopBox");
    let rconconsole = $("#consoleBox");
    let consoleBottom = $("#consoleBottom")
    let aicmd = $("#aicmd");
    let rconcmd = $("#rconcmd");
    let sendaicmd = $("#sendaicmd");
    let sendrconcmd = $("#sendrconcmd");
    
    let scroll = $("#enableScroll");
    let killswitch = $("#killSwitch");

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
        
    aicmd.on("keydown",     {"type": "ai", "message": aicmd},       enterCmd);
    rconcmd.on("keydown",   {"type": "rcon", "message": rconcmd},   enterCmd);
    sendaicmd.on("click",   {"type": "ai", "message": aicmd},       sendCmd);
    sendrconcmd.on("click", {"type": "rcon", "message": rconcmd},   sendCmd);
    killswitch.on("click", killSwitchChanged);

    socket.on("consoleget", (data) => {
        if (rconconsole.text() == data) {
            return;
        }
        if (scroll.is(":checked")) {
            console.log("yes");
            consoleBottom.get()[0].scrollIntoView();
        }
        rconconsole.html(data); 
    });
    killSwitchChanged();
});