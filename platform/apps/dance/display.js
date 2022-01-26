import { DanceLesson } from "./components/dance.js"

export const dance = new p5(( sketch ) =>{
    sketch.name = "dance"
    sketch.z_index = 0
    sketch.activated = false

    sketch.set = (width, height, socket) => {
        sketch.selfCanvas = sketch.createCanvas(width, height).position(0, 0).style("z-index", sketch.z_index);

        sketch.dance_lesson = new DanceLesson("dance02", sketch)
        socket.on(sketch.name, (data) => {
            sketch.dance_lesson.update_data(data)
        });

        sketch.angleMode(RADIANS);
        sketch.textAlign(CENTER, CENTER);

        sketch.activated = true;
    }

    sketch.resume = () => {
        sketch.dance_lesson.reset();
    };

    sketch.pause = () => {};

    sketch.windowResized = () => {
        sketch.resizeCanvas(windowWidth, windowHeight);
    }

    sketch.update = () => {
        sketch.dance_lesson.update(sketch)
    }

    sketch.show = () => {
        if (!sketch.activated) return;
        sketch.clear();
        sketch.dance_lesson.show(sketch);
    }
});
