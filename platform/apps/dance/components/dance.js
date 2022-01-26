export class DanceLesson {
    constructor(file_name, sketch) {
        this.body_pose = [];
        this.indexes_to_study = [0, 11, 12, 15, 16, 23, 24];

        this.init = false;
        this.offset = [0, 0];
        this.ratio = 1;
        this.size = [];
        this.length = 1000; // Arbitrary

        this.video = sketch.loadImage("/apps/dance/components/videos/" + file_name + ".gif");
        this.video.pause();
        this.video_index = 0;
        this.loaded = false;

        this.moves = sketch.loadJSON(
            "/apps/dance/components/movements/" + file_name + ".json", // Structure : moves["index"] = [[kpts_index, x, y], ...]
            (moves) => {
                sketch.dance_lesson.size = moves["size"]; // Original video size
                sketch.dance_lesson.length = moves["length"]; // Original video size
                sketch.dance_lesson.loaded = true;
            });
        this.moves_index = 0;

        this.diff = 0; // The lower, the closer the moves are
        this.limit = 120; // if this.diff < this.limit, it goes on
        this.time = 0;
        this.timelimit = 360;
    }

    reset() {
        this.time = 0;
        this.moves_index = 0;
        this.video_index = 0;
        this.diff = 0;
        this.offset = [0, 0];
        this.ratio = 1;
        this.size = this.moves["size"];
        this.init = false;
    }

    update_data(body_pose) {
        this.body_pose = body_pose;
    }

    show(sketch) {
        if (this.init && this.moves_index > this.video_index) {
            this.video_index++;
        }
        this.video.pause();
        this.video.setFrame(this.video_index);
        sketch.image(
            this.video,
            this.offset[0],
            this.offset[1],
            this.size[0],
            this.size[1]
        );

        sketch.stroke(255);
        sketch.fill(255);
        sketch.strokeWeight(2);
        sketch.textSize(30);
        sketch.text(
            Math.floor(this.diff),
            80,
            80
        );



        sketch.noStroke();
        if (this.diff < this.limit) {
            sketch.fill('rgb( 166,216,84)');
        } else {
            sketch.fill('rgb( 215,25,28)');
        }
        let rect_height = min(this.diff * 3, sketch.height - 50 - 400);

        // console.log(rect_height);
        sketch.rect(
            65,
            sketch.height - 50 - rect_height,
            30,
            rect_height
        );
        sketch.stroke(255);
        sketch.strokeWeight(2);
        sketch.line(
            60, sketch.height - 50 - 3*this.limit,
            100, sketch.height - 50 - 3*this.limit
            )


        sketch.push();

        sketch.translate(80, 180); // Center
        sketch.rotate(-PI/2);
        sketch.stroke(255);
        sketch.strokeWeight(2);
        sketch.fill(255);
        sketch.arc(
            0, 0,
            60, 60, //Diameter
            0, (1 - this.time / this.timelimit) * TWO_PI //Angle
        )
        sketch.noFill();
        sketch.arc(
            0, 0,
            90, 90, //Diameter
            0, (1 - this.time / this.timelimit) * TWO_PI //Angle
        )

        sketch.pop();

    }

    update(sketch) {
        if (this.moves_index >= this.length - 5) {
            sketch.selfCanvas.clear();
            sketch.activated = false;
            this.reset();
            return;
        }
        if (this.body_pose == undefined || this.body_pose.length <= 0) return;
        if (!this.loaded) return;

        if (!this.init) {
            this.init = true;

            let mirror_nose_reference = this.body_pose[0].slice(0, 2); // Current nose postion of the user
            let mirror_left_hip_reference = this.body_pose[24].slice(0, 2); // Current left hip postion of the user
            let video_nose_reference = this.moves[Object.keys(this.moves)[0]][0].slice(1, 3); // Position in pixels of the first nose of this.moves
            let video_left_hip_reference = this.moves[Object.keys(this.moves)[0]][23].slice(1, 3); // Position in pixels of the first left_hip of this.moves

            let mirror_distance = sketch.dist( //Nose Hip in the mirror
                mirror_nose_reference[0],
                mirror_nose_reference[1],
                mirror_left_hip_reference[0],
                mirror_left_hip_reference[1]
            );

            let video_distance = sketch.dist( //Nose hip in the video
                video_nose_reference[0],
                video_nose_reference[1],
                video_left_hip_reference[0],
                video_left_hip_reference[1]
            );

            this.ratio = mirror_distance / video_distance;
            this.size = [
                this.size[0] * this.ratio,
                this.size[1] * this.ratio
            ];

            this.offset = [
                mirror_nose_reference[0] - video_nose_reference[0] * this.ratio,
                mirror_nose_reference[1] - video_nose_reference[1] * this.ratio
            ];

        } else {
            this.time++;
            if (this.time > this.timelimit) {
                sketch.selfCanvas.clear();
                sketch.activated = false;
                this.reset();
                return;
            }
            if (this.moves_index in this.moves) {
                let distances = [];
                for (let i = 0; i < this.indexes_to_study.length; i++) {
                    distances.push(
                        sketch.dist(
                            this.offset[0] + this.moves[this.moves_index][this.indexes_to_study[i]][1] * this.ratio, //Video x
                            this.offset[1] + this.moves[this.moves_index][this.indexes_to_study[i]][2] * this.ratio, //Video y
                            this.body_pose[this.indexes_to_study[i]][0], //Mirror x
                            this.body_pose[this.indexes_to_study[i]][1], //Mirror y
                        )
                    );
                }
                this.diff = distances.reduce((partial_sum, a) => partial_sum + a, 0) / distances.length; //Mean of kpts differences
                if (this.diff < this.limit) {
                    this.moves_index++;
                    this.time = max(0, this.time - 5);
                }
            } else {
                this.moves_index++;
            }
        }

    }
}
