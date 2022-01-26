export const clock = new p5((sketch) => {
    sketch.name = "clock";
    sketch.z_index = 0
    sketch.activated = false;

    let r;
    const ec = 10;

    let eh, emin, esec, emilli;
    let h, min, sec, milli;

    sketch.set = (width, height, socket) => {
        sketch.width = 200;
        sketch.height = 200;
        sketch.x = width - sketch.width;
        sketch.y = 0;
        sketch.selfCanvas = sketch.createCanvas(
            sketch.width,
            sketch.height
        ).position(
            sketch.x,
            sketch.y
        ).style("z-index", sketch.z_index);

        r = sketch.min(sketch.width, sketch.height) * 0.5 - 3 * ec;
        sketch.angleMode(DEGREES);
        sketch.activated = true;
    };

    sketch.resume = () => {};

    sketch.pause = () => {};

    sketch.update = () => {};

    sketch.show = () => {
        sketch.clear();
        sketch.push();
        sketch.translate(sketch.width / 2, sketch.height / 2);
        sketch.rotate(-90);
        h = sketch.hour();
        min = sketch.minute();
        sec = sketch.second();
        milli = sketch.millis();

        sketch.strokeWeight(3);
        eh = sketch.map(h % 12, 0, 12, 0, 360);
        sketch.noFill();
        sketch.stroke(76, 0, 153);
        sketch.arc(0, 0, 2 * r, 2 * r, 0, eh);

        sketch.push();
        sketch.rotate(eh);
        sketch.stroke(76, 0, 153);
        sketch.line(0, 0, r * 0.4, 0);
        sketch.pop();

        emin = sketch.map(min, 0, 60, 0, 360);
        sketch.noFill();
        sketch.stroke(200, 200, 0);
        sketch.arc(0, 0, 2 * r + ec, 2 * r + ec, 0, emin);

        sketch.push();
        sketch.rotate(emin);
        sketch.stroke(200, 200, 0);
        sketch.line(0, 0, r * 0.6, 0);
        sketch.pop();

        esec = sketch.map(sec, 0, 60, 0, 360);
        sketch.noFill();
        sketch.stroke(50, 150, 255);
        sketch.arc(0, 0, 2 * r + 2 * ec, 2 * r + 2 * ec, 0, esec);

        sketch.push();
        sketch.rotate(esec);
        sketch.stroke(50, 150, 255);
        sketch.line(0, 0, r * 0.8, 0);
        sketch.pop();

        emilli = sketch.map(milli, 0, 1000, 0, 360);
        sketch.noFill();
        sketch.stroke(100, 255, 200);
        sketch.arc(0, 0, 2 * r + 3 * ec, 2 * r + 3 * ec, 0, emilli);

        // sketch.push();
        // sketch.rotate(emilli);
        // sketch.stroke(100, 255, 200);
        // sketch.line(0,0,r * 0.9,0);
        // sketch.pop();
        sketch.pop();
    };
});
