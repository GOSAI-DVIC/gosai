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

socket_link = socket;

socket.on("core-app_manager-start_application", async (data) => {
    const application_name = data["application_name"];

    if (Object.keys(modules).includes(application_name)) {
        if (!modules[application_name].activated) {
            try {
                modules[application_name].activated = true;
                modules[application_name].selfCanvas.show();
                modules[application_name].resume();
            } catch (e) {
                catch_error(e, application_name, "Resume error", true);
            }
        }
    } else {
        try {
            const module = await import("./home/apps/" + application_name + "/display.js")
            const application = module[application_name]
            console.log("Starting:" + application_name);
            application.set(window.innerWidth, window.innerHeight, socket);
            modules[application_name] = application;
        } catch (e) {
            catch_error(e, application_name, "Start error", true);
        }
    }

    socket.emit("application-" + application_name + "-started");
});

socket.on("core-app_manager-stop_application", async (data) => {
    const application_name = data["application_name"];

    try {
        console.log("Stopping:" + application_name);
        if(Object.keys(modules).includes(application_name)) {
            modules[application_name].activated = false;
            modules[application_name].selfCanvas.hide();
            modules[application_name].pause();
        }
    } catch (e) {
        catch_error(e, application_name, "Stop error", false);
    }

});

socket.emit("core-app_manager-window_loaded");

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
