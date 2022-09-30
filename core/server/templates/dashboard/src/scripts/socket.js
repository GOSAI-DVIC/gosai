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

socket.on("core-logger-log_history", (data) => {
    history = data["history"];
    generate_console_logs();
});

socket.on("core-logger-log", (log) => {
    add_to_logs(log);
});

socket.on("core-app_manager-available_applications", (data) => {
    let applications = data["applications"];
    generate_applications_table(applications)
});

socket.on("core-hal-available_drivers", (data) => {
    let drivers = data["drivers"];
    generate_drivers_table(drivers);
});

socket.on("core-server-connected_users", (data) => {
    let clients = data["users"];
    generate_clients_table(clients);
    let display = document.getElementById("clients-stats-connected");
    display.innerText = Object.keys(clients).length;
});

socket.on("core-system_monitor-display_statistics", (data) => {
    update_fps_chart({
        x: data["time"],
        y: data["fps"]
    });
    update_ms_chart({
        timestamp: data["time"],
        data: data["modules_consumptions"]
    });
});

socket.on("core-system_monitor-recent_performances", data => {
    // socket.emit("purge_recent_performances");
    let drivers_performances = data["performances"]["driver"];
    if (drivers_performances != undefined){
        update_drivers_lp_chart({
            timestamp: Date.now(),
            data: drivers_performances
        });
        update_drivers_nlp_chart({
            timestamp: Date.now(),
            data: drivers_performances
        });
    }
})

socket.emit("core-logger-get_log_history");
socket.emit("core-app_manager-get_available_applications");
socket.emit("core-hal-get_available_drivers");
socket.emit("core-server-get_users");
setInterval(() => {
    socket.emit("core-logger-get_recent_performances");
}, 500);
