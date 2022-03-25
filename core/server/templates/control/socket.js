socket = io.connect('ws://' + window.location.host, {
    cors: {
        origin: "ws://" + window.location.host,
        methods: ["GET", "POST"]
    },
    transports: ["websocket"]
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

socket.on("start_application", async (data) => {
    let new_app = data["application_name"]
    update_app_button(new_app, 1)
});

socket.on("stop_application", async (data) => {
    let new_app = data["application_name"]
    update_app_button(new_app, 0)
});