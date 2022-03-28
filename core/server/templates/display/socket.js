let path_parameter = window.location.pathname.split('/');
path_parameter.splice(-1);
const path = path_parameter.join('/');

export const socket = io.connect('ws://' + window.location.host, {
    path: path + "/socket.io",
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    },
    transports: ["websocket"]
});

socket.on("start_application", async (data) => {
    const application_name = data["application_name"];

    if (Object.keys(modules).includes(application_name)) {
        if (!modules[application_name].activated) {
            modules[application_name].activated = true;
            modules[application_name].selfCanvas.show();
            modules[application_name].resume();
        }
    } else {
        const module = await import("./home/apps/" + application_name + "/display.js")

        const application = module[application_name]

        console.log("Starting:" + application_name);

        application.set(width, height, socket);
        modules[application_name] = application;
    }

    socket.emit("started_" + application_name);
});

socket.on("stop_application", async (data) => {
    const application_name = data["application_name"];

    console.log("Stopping:" + application_name);

    modules[application_name].activated = false;
    modules[application_name].selfCanvas.hide();
    modules[application_name].pause();
});

socket.emit("window_loaded");
