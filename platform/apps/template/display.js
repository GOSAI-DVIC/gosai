export const template = new p5(( sketch ) => {
    sketch.name = "template"
    sketch.z_index = 0
    sketch.activated = false

    sketch.set = (width, height, socket) => {
        sketch.selfCanvas = sketch.createCanvas(width, height).position(0, 0).style("z-index", sketch.z_index);

        socket.on("template", (data) => {

        });
    }

    sketch.windowResized = () => {
        sketch.resizeCanvas(windowWidth, windowHeight);
    }

    sketch.resume = () => {};

    sketch.pause = () => {};

    sketch.update = () => {}

    sketch.show = () => {
        sketch.clear();
    }
});
