import { Game } from "./components/game.js"

export const bounce = new p5(( sketch ) =>{
    sketch.name = "bounce"
    sketch.z_index = 10
    sketch.activated = false

    sketch.set = (width, height, socket) => {
        sketch.selfCanvas = sketch.createCanvas(width, height).position(0, 0)//.style("z-index", sketch.z_index);

        sketch.game = new Game(sketch)
        socket.on(sketch.name, (data) => {
            sketch.game.update_data(
                data["left_hand_pose"],
                data["right_hand_pose"]
            )
        });

        sketch.angleMode(RADIANS);
        sketch.textAlign(CENTER, CENTER);

        sketch.activated = true;
    }

    sketch.resume = () => {
        sketch.game.reset();
    };

    sketch.pause = () => {

    };

    sketch.windowResized = () => {
        sketch.resizeCanvas(windowWidth, windowHeight);
    }

    sketch.update = () => {
        sketch.game.update(sketch)
    }

    sketch.show = () => {
        if (!sketch.activated) return;
        sketch.clear();
        sketch.game.show(sketch);
    }
});
