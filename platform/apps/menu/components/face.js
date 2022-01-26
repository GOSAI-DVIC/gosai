export class Face {
    constructor(name) {

        this.junctions = [
            // Lips.
            [
                61, 146, 146, 91, 91, 181, 181, 84, 84, 17, 17, 314, 314, 405, 405, 321,
                321, 375, 375, 291, 61, 185, 185, 40, 40, 39, 39, 37, 37, 0, 0, 267, 267,
                269, 269, 270, 270, 409, 409, 291, 78, 95, 95, 88, 88, 178, 178, 87, 87, 14,
                14, 317, 317, 402, 402, 318, 318, 324, 324, 308, 78, 191, 191, 80, 80, 81,
                81, 82, 82, 13, 13, 312, 312, 311, 311, 310, 310, 415, 415, 308
            ],
            // Left eye.
            [
                33, 7, 7, 163, 163, 144, 144, 145, 145, 153, 153, 154, 154, 155, 155, 133,
                33, 246, 246, 161, 161, 160, 160, 159, 159, 158, 158, 157, 157, 173, 173,
                133
            ],
            // Left eyebrow.
            [
                46, 53, 53, 52, 52, 65, 65, 55, 70, 63, 63, 105, 105, 66, 66, 107
            ],
            // Right eye.
            [
                263, 249, 249, 390, 390, 373, 373, 374, 374, 380, 380, 381, 381, 382, 382,
                362, 263, 466, 466, 388, 388, 387, 387, 386, 386, 385, 385, 384, 384, 398,
                398, 362
            ],
            // Right eyebrow.
            [
                276, 283, 283, 282, 282, 295, 295, 285, 300, 293, 293, 334, 334, 296, 296,
                336
            ],
            // Face oval.
            [
                10, 338, 338, 297, 297, 332, 332, 284, 284, 251, 251, 389, 389, 356, 356,
                454, 454, 323, 323, 361, 361, 288, 288, 397, 397, 365, 365, 379, 379, 378,
                378, 400, 400, 377, 377, 152, 152, 148, 148, 176, 176, 149, 149, 150, 150,
                136, 136, 172, 172, 58, 58, 132, 132, 93, 93, 234, 234, 127, 127, 162, 162,
                21, 21, 54, 54, 103, 103, 67, 67, 109, 109, 10
            ]
        ];

        this.face_mesh = [];
        this.transposed_face_mesh = [];

        this.name = name;

        this.showing = true;
        this.show_face_points = true;
        this.show_face_lines = true;
    }

    show(sketch) {
        if (!this.showing) return;
        sketch.push();
        sketch.fill(200);
        if (this.show_face_points) {
            for (let i = 0; i < this.transposed_face_mesh.length; i++) {
                sketch.ellipse(
                    this.transposed_face_mesh[i][0],
                    this.transposed_face_mesh[i][1],
                    4
                );
            }
        }

        sketch.stroke(255);
        sketch.strokeWeight(2);
        if (
            this.show_face_lines &&
            this.transposed_face_mesh.length > 0
        ) {

            this.junctions.forEach(parts => {
                for (let i = 0; i < parts.length - 1; i++) {
                    if (this.transposed_face_mesh[parts[i]][1] > 0 &&
                        this.transposed_face_mesh[parts[i + 1]][1] > 0) {
                        sketch.line(
                            this.transposed_face_mesh[parts[i]][0],
                            this.transposed_face_mesh[parts[i]][1],
                            this.transposed_face_mesh[parts[i + 1]][0],
                            this.transposed_face_mesh[parts[i + 1]][1]
                        );
                    }
                }
            });

        }

        sketch.pop();
    }

    update_data(data) {
        if (data != undefined) {
            this.transposed_face_mesh = data
        }
    }

    update() {

        if (this.face_mesh == []) {
            return
        }

        for (let i = 0; i < this.face_mesh.length; i++) {

            if (this.face_mesh[i] != [-1, -1]) {
                let x = width * (this.face_mesh[i][0] - xoffset) / screenwidth;
                let y = height * (this.face_mesh[i][1] - yoffset) / screenheight;

                this.transposed_face_mesh[i] = [x, y];

            } else {
                transposed.push([0, 0])
            }

        };

    }

}
