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
    update_fps_chart({
        x: data["time"],
        y: data["fps"]
    });
    update_ms_chart({
        timestamp: data["time"],
        data: data["modules_consumptions"]
    });
});

socket.on("recent_performances", data => {
    // socket.emit("purge_recent_performances");
    let drivers_performances = data["performances"]["driver"];
    if (drivers_performances != undefined){
        update_drivers_lp_chart({
            timestamp: Date.now(),
            data: data["performances"]["driver"]
        });
    }
})

socket.emit("get_log_history");
socket.emit("get_available_applications");
socket.emit("get_available_drivers");
socket.emit("get_users");
setInterval(() => {
    socket.emit("get_recent_performances");
}, 500);
