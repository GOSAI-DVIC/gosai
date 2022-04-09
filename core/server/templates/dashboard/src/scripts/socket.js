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
    let display = document.getElementById("applications-stats-available");
    display.innerText = applications.length;
});

socket.on("started_applications", (data) => {
    let applications = data["applications"];
    let display = document.getElementById("applications-stats-started");
    display.innerText = applications.length;
});

socket.on("stopped_applications", (data) => {
    let applications = data["applications"];
    let display = document.getElementById("applications-stats-stopped");
    display.innerText = applications.length;
});

socket.on("available_drivers", (data) => {
    let drivers = data["drivers"];
    let display = document.getElementById("drivers-stats-available");
    display.innerText = drivers.length;
});

socket.on("started_drivers", (data) => {
    let drivers = data["drivers"];
    let display = document.getElementById("drivers-stats-started");
    display.innerText = drivers.length;
});

socket.on("stopped_drivers", (data) => {
    let drivers = data["drivers"];
    let display = document.getElementById("drivers-stats-stopped");
    display.innerText = drivers.length;
});

socket.on("connected_users", (data) => {
    let clients = data["users"];
    let display = document.getElementById("clients-stats-connected");
    display.innerText = Object.keys(clients).length;
});

socket.emit("get_log_history");
socket.emit("get_available_applications");
socket.emit("get_started_applications");
socket.emit("get_stopped_applications");
socket.emit("get_available_drivers");
socket.emit("get_started_drivers");
socket.emit("get_stopped_drivers");
socket.emit("get_users");
