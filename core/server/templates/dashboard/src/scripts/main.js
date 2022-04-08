let history = [];

function generate_console_logs() {
    let logs = "";
    history.forEach(log => {
        logs += log_to_str(log);
    });
    document.getElementById("console-output").innerHTML = logs;
    document.getElementById("console-output").scrollTop = document.getElementById("console-output").scrollHeight;
}

function add_to_logs(log) {
    history.push(log);
    document.getElementById("console-output").innerHTML += log_to_str(log);
    document.getElementById("console-output").scrollTop = document.getElementById("console-output").scrollHeight;
}

function log_to_str(data) {
    let level_color = "";
    switch (data["level"]) {
        case 3:
            level_color = "level-warning";
            break;
        case 4:
            level_color = "level-error";
            break;
        default:
            level_color = "level-info";
            break;
    }
    let result = "<span class='" + level_color + "'>" + data["time"] + " : " + data["level"] + " : " + data["source"] + "</span> : " + data["content"] + "<br>";
    return result.replace(/\n/g, "<br />");
}

function send_command() {
    let command = document.getElementById("console-input").value;
    socket.emit("execute_command", {"command": command});
    document.getElementById("console-input").value = "";
}

function do_send(event) {
    if(event.key === 'Enter') {
        send_command();
    }
}
