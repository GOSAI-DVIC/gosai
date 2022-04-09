let history = [];
let command_history = [];
let current_command = 0;
let command_index = -1;

function generate_console_logs() {
    let logs = "";
    history.forEach((log) => {
        logs += log_to_str(log);
    });
    document.getElementById("console-output").innerHTML = logs;
    document.getElementById("console-output").scrollTop =
        document.getElementById("console-output").scrollHeight;
}

function add_to_logs(log) {
    history.push(log);
    document.getElementById("console-output").innerHTML += log_to_str(log);
    document.getElementById("console-output").scrollTop =
        document.getElementById("console-output").scrollHeight;
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
    let result =
        "<span class='" +
        level_color +
        "'>" +
        data["time"] +
        " : " +
        data["level"] +
        " : " +
        data["source"] +
        "</span> : " +
        data["content"] +
        "<br>";
    return result.replace(/\n/g, "<br />");
}

function send_command() {
    let command = document.getElementById("console-input").value;
    socket.emit("execute_command", { command: command });
    command_history.push(command);
    current_command = "";
    command_index = -1;
    document.getElementById("console-input").value = "";
}

function key_action(event) {
    switch (event.key) {
        case "Enter":
            send_command();
            break;
        case "ArrowUp":
            if (command_index == -1 && command_history.length > 0) {
                current_command =
                    document.getElementById("console-input").value;
                command_index = command_history.length - 1;
                document.getElementById("console-input").value =
                    command_history[command_index];
            } else if (command_index > 0) {
                command_index--;
                document.getElementById("console-input").value =
                    command_history[command_index];
            }
            break;
        case "ArrowDown":
            if (command_index == command_history.length - 1 && command_index != -1) {
                command_index = -1;
                document.getElementById("console-input").value =
                    current_command;
            } else if (command_index < command_history.length - 1 && command_index != -1) {
                command_index++;
                document.getElementById("console-input").value =
                    command_history[command_index];
            }
            break;
        default:
            break;
    }
}

function generate_clients_table(clients) {
    sids = Object.keys(clients);
    document.getElementById("clients-table-body").innerHTML = "";
    console.log(clients)
    for (let i = 0; i < sids.length; i++){
        let row = document.createElement("tr");
        let sid = sids[i];

        let sid_cell = document.createElement("td");
        sid_cell.innerHTML = sid;
        row.appendChild(sid_cell);

        let ip_cell = document.createElement("td");
        ip_cell.innerHTML = clients[sid]["address"];
        row.appendChild(ip_cell);

        let source_cell = document.createElement("td");
        source_cell.innerHTML = clients[sid]["source"];
        row.appendChild(source_cell);

        let time_cell = document.createElement("td");
        time_cell.innerHTML = clients[sid]["time"];
        row.appendChild(time_cell);
        document.getElementById("clients-table-body").appendChild(row);
    }

}

function generate_table_from_list(table_id, list) {
    document.getElementById(table_id).innerHTML = "";
    for (let i = 0; i < list.length; i++) {
        let row = document.createElement("tr");

        let name_cell = document.createElement("td");
        name_cell.innerHTML = list[i];
        row.appendChild(name_cell);

        document.getElementById(table_id).appendChild(row);
    }
}
