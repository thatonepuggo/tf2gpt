$(function() {
    var socket = io();

    let refreshTime = $("#refreshTime");
    let info = $("#info");

    let rconconsole = $("#console");
    let aicmd = $("#aicmd");
    let rconcmd = $("#rconcmd");
    let sendaicmd = $("#sendaicmd");
    let sendrconcmd = $("#sendrconcmd");
    
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
        
    aicmd.on("keydown",     {"type": "ai", "message": aicmd},       enterCmd);
    rconcmd.on("keydown",   {"type": "rcon", "message": rconcmd},   enterCmd);
    sendaicmd.on("click",   {"type": "ai", "message": aicmd},       sendCmd);
    sendrconcmd.on("click", {"type": "rcon", "message": rconcmd},   sendCmd);

    socket.on("consoleget", (data) => {
        rconconsole.html(data);
    })
})