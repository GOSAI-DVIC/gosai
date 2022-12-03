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

let config;
let doCalibration = false;
let calibrationData;
let calibrationMatrix;

function preload() {
    let url = getURLPath();
    url.splice(-1);
    url = url.join("/");
    config = loadJSON("/" + url + "/platform/home/config.json",
        (data) => {
            if (data.calibrate) {
                calibrationData = loadJSON("/" + url + "/platform/home/calibration_data.json");
                doCalibration = true;
            }
    });
}

function setup() {
    canvas = createCanvas(window.innerWidth, window.innerHeight);
    frameRate(120);

    if(doCalibration) {
        calibrationMatrix = new ProjectionMatrix(
            calibrationData.outpts,
            calibrationData.screen_coords
        );
        calibrationMatrix.edit = true;
    }
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
                if(doCalibration) {
                    module.push();
                    calibrationMatrix.apply(module, 2);
                    // module.clear();
                    module.show();
                    module.pop();
                }
                else {
                    module.show();
                }
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
    socket_link.emit("core-app_manager-log_for_application", {
        source: module_name,
        content: prefix + ": " + error.toString(),
        level: 4,
    });
    if (!stop) return;
    socket_link.emit("core-app_manager-stop_application", {
        application_name: module_name,
    });
}
