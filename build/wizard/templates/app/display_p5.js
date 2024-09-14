
export const template_app = new p5((sketch) => {
    sketch.name = "template_app";
    sketch.activated = false;

    // Change the z-index to display the app on top of the others or behind them
    sketch.z_index = 5;

    // Called on the creation of the app
    sketch.preload = () => {};

    // Called on the creation of the app by GOSAI
    sketch.set = (width, height, socket) => {
        sketch.width = width;
        sketch.height = height;
        sketch.socket = socket;

        sketch.selfCanvas = sketch
            .createCanvas(width, height)
            .position(0, 0)
            .style("z-index", sketch.z_index);


        // socket.on("<event_data_name>", (data) => { console.log(data) });

        // The app won't be shown until sketch.activated is set to true
        sketch.activated = true;
    };

    // Called when the screen is resized
    sketch.windowResized = () => resizeCanvas(windowWidth, windowHeight);

    // Called when the app is paused
    sketch.pause = () => {};

    // Called when the app is resumed
    sketch.resume = () => {};

    // Called on every frame, before show()
    sketch.update = () => {};

    // Called on every frame, after update()
    sketch.show = () => {
        sketch.clear();
        //Draw here
    };
});
