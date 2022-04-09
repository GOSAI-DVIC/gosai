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
    transports: ["websocket"],
    query: "source=control"
});

socket.on("available_applications", async (data) => {
    app = data["applications"]
    create_app_button(app)
});

socket.on("started_applications", async (data) => {
    let started_apps = data["applications"];
    started_apps.forEach(app_name => {
        update_app_button(app_name, 1)
    });
});

socket.on("stopped_applications", async (data) => {
    let stopped_apps = data["applications"];
    stopped_apps.forEach(app_name => {
        update_app_button(app_name, 0)
    });
});

socket.on("sound",() => {
    speaker_request = true;
})
