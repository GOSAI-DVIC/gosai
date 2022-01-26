const socket = io.connect('ws://0.0.0.0:5000', {
    cors: {
        origin: "ws://0.0.0.0:5000",
        methods: ["GET", "POST"]
    },
    transports: ["websocket"]
});

socket.on("start_application", async (data) => {
    const application_name = data["application_name"];

    if(Object.keys(modules).includes(application_name)) {
        modules[application_name].activated = true;
        modules[application_name].selfCanvas.show();
        modules[application_name].resume();
    } else {
        const module = await import("/platform/apps/" + application_name  + "/display.js")

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
