let history = [];

function generate_console_logs() {
    let logs = "";
    history.forEach(log => {
        logs += log_to_str(log);
    });
    document.getElementById("console-output").innerText = logs;
}

function add_to_logs(log) {
    history.push(log);
    document.getElementById("console-output").innerText += log_to_str(log);
}

function log_to_str(data) {
    return data["time"] + " : " + data["level"] + " : " + data["source"] + " : " + data["content"] + "\n";
}

function send_command() {
    let command = document.getElementById("command-input").value;
    socket.emit("command", command);
}
