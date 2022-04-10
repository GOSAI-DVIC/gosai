let modules = {};

let stats = {};
let modules_consumptions = {};

let canvas;

const xoffset = -260; // millimeters
const yoffset = 70;

const screenwidth = 392.85; //millimeters
const screenheight = 698.4;

let global_data = {};
let recieved = false;

function setup() {
    canvas = createCanvas(windowWidth, windowHeight);
    frameRate(120);
}

function draw() {
    background(0);

    for (const [name, module] of Object.entries(modules)) {
        let start = window.performance.now();
        if (module.activated) {
            module.update();
            module.show();
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
