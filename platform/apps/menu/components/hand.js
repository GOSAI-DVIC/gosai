export class Hand {
    constructor(hand_name) {
        this.junctions = [
            [
                [0, 1],
                [0, 5],
                [0, 9],
                [0, 13],
                [0, 17],
                [5, 9],
                [9, 13],
                [13, 17]
            ],
            [
                [1, 2],
                [2, 3],
                [3, 4]
            ],
            [
                [5, 6],
                [6, 7],
                [7, 8]
            ],
            [
                [9, 10],
                [10, 11],
                [11, 12]
            ],
            [
                [13, 14],
                [14, 15],
                [15, 16]
            ],
            [
                [17, 18],
                [18, 19],
                [19, 20]
            ]
        ];

        this.keypoints = [
            0, 1, 2, 3, 4, 5,
            6, 7, 8, 9, 10, 11,
            12, 13, 14, 15, 16,
            17, 18, 19, 20
        ];

        this.hand_pose = [];

        this.hand_name = hand_name;

        this.showing = true;
        this.show_hands_points = false;
        this.show_hands_lines = true;

        this.sign = ["NONE", 0];
    }

    show(sketch) {
        if (!this.showing) return;
        sketch.push();

        sketch.fill(200);
        if (this.show_hands_points) {
            for (let i = 0; i < this.hand_pose.length; i++) {
                sketch.ellipse(
                    this.hand_pose[i][0],
                    this.hand_pose[i][1],
                    10
                );
            }
        }

        sketch.stroke(255);
        sketch.strokeWeight(4);
        if (
            this.show_hands_lines &&
            this.hand_pose.length  == this.keypoints.length
        ){
            this.junctions.forEach(parts => {
                parts.forEach(pair => {
                    print(this.hand_pose[pair[0]][3])
                    if (
                        this.hand_pose[pair[0]][3] >= 0 &&
                        this.hand_pose[pair[0]][1] > 0 &&
                        this.hand_pose[pair[1]][1] > 0
                    ) {
                        sketch.line(
                            this.hand_pose[pair[0]][0],
                            this.hand_pose[pair[0]][1],
                            this.hand_pose[pair[1]][0],
                            this.hand_pose[pair[1]][1]
                        );
                    }
                })
            })
        }

        sketch.pop();
    }

    update_data(pose, sign) {
        if (pose != undefined && pose.length > 0) {
            this.hand_pose = pose
        }
        if (sign != undefined) {
            this.sign = sign
        }
    }

    update() {

        // if (this.hand_pose == []) {
        //     return
        // }

        // for (let i = 0; i < this.hand_pose.length; i++) {

        //     if (this.hand_pose[i] != [-1, -1]) {
        //         let x = width * (this.hand_pose[i][0] - xoffset) / screenwidth;
        //         let y = height * (this.hand_pose[i][1] - yoffset) / screenheight;

        //         if (this.transposed_hand_pose.length > i) {
        //             let newx = width * (this.hand_pose[i][0] - xoffset) / screenwidth;
        //             let newy = height * (this.hand_pose[i][1] - yoffset) / screenheight;

        //             if (newy > 0 || this.transposed_hand_pose[i][1] < 0) {
        //                 x = lerp(this.transposed_hand_pose[i][0], newx, 0.8);
        //                 y = lerp(this.transposed_hand_pose[i][1], newy, 0.8);
        //             } else { // Assume it's an artifact and slows the update
        //                 x = lerp(this.transposed_hand_pose[i][0], newx, 0.01);
        //                 y = lerp(this.transposed_hand_pose[i][1], newy, 0.01);
        //             }
        //         }

        //         this.transposed_hand_pose[i] = [x, y];

        //     } else {
        //         this.transposed_hand_pose.push([0, 0])
        //     }

        // };

    }

}
