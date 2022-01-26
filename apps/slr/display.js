import { Slr } from "./components/slr.js"

export const slr = new  p5(( sketch ) => {
    sketch.name = "slr"
    sketch.z_index = 0
    sketch.activated = false

    sketch.set = (width, height, socket) => {
        sketch.selfCanvas = sketch.createCanvas(width, height).position(0, 0).style("z-index", sketch.z_index);

        sketch.slr = new Slr(sketch)
        socket.on(sketch.name, (data) => {
            sketch.slr.update_data(
                data["sign"],
                data["probability"]
            )
            console.log(data["sign"])
        });
        
        sketch.activated = true;
    }
    
    sketch.resume = () => {
        sketch.slr.reset();
    };

    sketch.pause = () => {};

    sketch.update = () => {
        sketch.slr.update()
    }

    sketch.show = () => {
        if (!sketch.activated) return;
        sketch.clear();
        sketch.slr.show(sketch);
    }
});
