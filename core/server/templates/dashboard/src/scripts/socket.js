let path_parameter = window.location.pathname.split("/");
path_parameter.splice(-1);
const path = path_parameter.join("/");

const socket = io.connect(window.location.origin, {
    path: path + "/socket.io",
    cors: {
        origin: "*",
        methods: ["GET", "POST"],
    },
    agent: false,
    upgrade: false,
    rejectUnauthorized: false,
    transports: ["websocket"],
    query: "source=dashboard"
});

socket.on("log_history", (data) => {
    history = data["history"];
    generate_console_logs();
});

socket.on("log", (log) => {
    add_to_logs(log);
});

socket.on("available_applications", (data) => {
    let applications = data["applications"];
    generate_applications_table(applications)
});

socket.on("available_drivers", (data) => {
    let drivers = data["drivers"];
    generate_drivers_table(drivers);
});

socket.on("connected_users", (data) => {
    let clients = data["users"];
    generate_clients_table(clients);
    let display = document.getElementById("clients-stats-connected");
    display.innerText = Object.keys(clients).length;
});

socket.on("display_statistics", (data) => {
    update_fps_chart({x : data["time"], y : data["fps"]});
});

socket.emit("get_log_history");
socket.emit("get_available_applications");
socket.emit("get_available_drivers");
socket.emit("get_users");
