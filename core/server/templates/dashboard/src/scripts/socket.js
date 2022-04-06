let path_parameter = window.location.pathname.split('/');
path_parameter.splice(-1);
const path = path_parameter.join('/');

const socket = io.connect(window.location.origin, {
    path: path + "/socket.io",
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    },
	agent: false,
	upgrade: false,
	rejectUnauthorized: false,
    transports: ["websocket"]
});

socket.on("log_history", data => {
    history = data["history"];
    generate_console_logs();
})

socket.on("log", log => {
    add_to_logs(log);
});

socket.emit("get_log_history");
