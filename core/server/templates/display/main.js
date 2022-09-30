let modules = {};
let socket_link;

let stats = {};
let modules_consumptions = {};

let canvas;

const xoffset = -260; // millimeters
const yoffset = 70;

const screenwidth = 392.85; //millimeters
const screenheight = 698.4;

let global_data = {};

function setup() {
    canvas = createCanvas(window.innerWidth, window.innerHeight);
    frameRate(120);
}

function draw() {
    background(0);

    for (const [name, module] of Object.entries(modules)) {
        let start = window.performance.now();
        if (module.activated) {
            try {
                module.update();
            } catch (e) {
                catch_error(e, module.name, "Update error", true);
            }
            try {
                module.show();
            } catch (e) {
                catch_error(e, module.name, "Show error", true);
            }
        }
        let end = window.performance.now();
        record_performance(name, end - start);
    }
}

function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
}

function record_performance(module_name, time) {
    if (modules_consumptions[module_name] == undefined) {
        modules_consumptions[module_name] = [];
    }
    modules_consumptions[module_name].push(time);
    if (modules_consumptions[module_name].length > 100) {
        modules_consumptions[module_name].shift();
    }
}

function catch_error(error, module_name, prefix = "", stop = true) {
    console.error(error);
    if (Object.keys(modules).includes(module_name))
        modules[module_name].activated = false;
    socket_link.emit("log_for_application", {
        source: module_name,
        content: prefix + ": " + error.toString(),
        level: 4,
    });
    if (!stop) return;
    socket_link.emit("stop_application", {
        application_name: module_name,
    });
}
