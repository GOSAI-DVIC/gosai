export class Game {
    constructor(sketch) {
        this.width = width * 0.8;
        this.height = height * 0.5;
        this.xoffset = width * 0.1;
        this.yoffset = 100;

        this.radius = 60;

        this.ball = new createVector(
            this.xoffset + random(this.width),
            this.yoffset + random(this.height)
        );
        this.count = 0;
        this.best = 0;
        this.limit = 30;
        this.timelimit = 20;
        this.starttime = millis();
        this.time = 0;

        this.left_hand_index;
        this.right_hand_index;
    }

    reset() {

        if(this.count > this.best) this.best = this.count;
        this.count = 0;
        this.starttime = millis();
        this.ball = new createVector(
            this.xoffset + random(this.width),
            this.yoffset + random(this.height)
        );
    }

    update_data(left_hand_pose, right_hand_pose) {
        if (left_hand_pose != undefined && left_hand_pose.length > 0) {
            this.left_hand_index = left_hand_pose[8].slice(0, 2);
        }
        if (right_hand_pose != undefined && right_hand_pose.length > 0) {
            this.right_hand_index = right_hand_pose[8].slice(0, 2);
        }
    }

    show(sketch) {

        sketch.stroke(255);
        sketch.fill(51, 153, 255);
        sketch.strokeWeight(15);
        sketch.circle(this.ball.x, this.ball.y, 2*this.radius);

        sketch.stroke(255);
        sketch.fill(255);
        sketch.strokeWeight(2);
        sketch.textSize(25);
        sketch.text(
            "Score: " + Math.floor(this.count),
            width - 100,
            250
        );

        sketch.text(
            "Best score: " + Math.floor(this.best),
            width - 100,
            300
        );

        sketch.push();

        sketch.translate(width - 100, 400); // Center
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
        this.time = (millis() - this.starttime)/1000;
        if (this.time >= this.timelimit) {
            this.reset();
        }
        if (this.right_hand_index == undefined || this.right_hand_index.length <= 0) {
            this.right_hand_index = [-100, -100];
        }
        if (this.left_hand_index == undefined || this.left_hand_index.length <= 0) {
            this.left_hand_index = [-100, -100];
        }

        let d = min(
            dist(this.ball.x, this.ball.y, this.left_hand_index[0], this.left_hand_index[1]),
            dist(this.ball.x, this.ball.y, this.right_hand_index[0], this.right_hand_index[1])
        );
        if (d < this.radius) {
            this.count += 1;
            this.ball = new createVector(
                this.xoffset + random(this.width),
                this.yoffset + random(this.height)
            );
        }
    }
}
