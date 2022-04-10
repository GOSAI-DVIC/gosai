let path_parameter = window.location.pathname.split('/');
path_parameter.splice(-1);
const path = path_parameter.join('/');

export const socket = io.connect(window.location.origin, {
    path: path + "/socket.io",
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    },
	agent: false,
	upgrade: false,
	rejectUnauthorized: false,
    transports: ["websocket"],
    query: "source=display"
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

let fps = 0;
let fps_prev_millis = 0;
let fps_prev_frameCount = 0;

setInterval(() => {
    fps = 1000 * (frameCount - fps_prev_frameCount) / (window.performance.now() - fps_prev_millis);

    stats = {
        "fps": fps,
        "frameCount": frameCount,
        "time": Date.now(),
        "modules_consumptions": modules_consumptions
    }
    socket.emit("set_display_statistics", stats);
    fps_prev_millis = window.performance.now();
    fps_prev_frameCount = frameCount;
    modules_consumptions = {};

}, 500);
