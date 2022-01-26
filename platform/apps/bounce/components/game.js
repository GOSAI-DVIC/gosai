export class Game {
    constructor(sketch) {
        this.radius = 60;

        this.ball = new createVector(width / 2, 60);

        this.speed = new createVector(0, 0);
        this.acc = new createVector(0, 2000);

        this.left_hand_pose;
        this.right_hand_pose;

        this.prev = millis();
        this.rebounded = false;
        this.rebound_factor = 0.95;
    }

    reset() {
        this.ball = new createVector(width / 2, 60);

        this.speed = new createVector(0, 0);
        this.acc = new createVector(0, 2000);

        this.prev = millis();
        this.rebounded = false;
    }

    update_data(left_hand_pose, right_hand_pose) {
        if (left_hand_pose != undefined && left_hand_pose.length > 0) {
            this.left_hand_pose = left_hand_pose;
        }
        if (right_hand_pose != undefined && right_hand_pose.length > 0) {
            this.right_hand_pose = right_hand_pose;
        }
    }

    show(sketch) {
        sketch.stroke(255, 100);
        sketch.fill(255, 60, 255);
        sketch.strokeWeight(30);
        sketch.circle(this.ball.x, this.ball.y, 2 * this.radius - 30);
    }

    update(sketch) {
        let dt = (millis() - this.prev) / 1000;
        let prev_speed = this.speed.copy();
        this.speed.add(new createVector(this.acc.x * dt, this.acc.y * dt));
        if (this.speed.y * prev_speed.y <= 0) this.rebounded = false;
        this.ball.add(new createVector(this.speed.x * dt, this.speed.y * dt));
        this.prev = millis();

        if (this.ball.y > height / 2 - this.radius) {
            this.speed.y *= -this.rebound_factor;
            this.ball.y = height / 2 - this.radius;
        }

        if (this.ball.x > width - this.radius) {
            this.speed.x *= -this.rebound_factor * 0.8;
            this.ball.x = width - this.radius;
        }

        if (this.ball.x < this.radius) {
            this.speed.x *= -this.rebound_factor * 0.8;
            this.ball.x = this.radius;
        }

        if (this.ball.y < this.radius) {
            this.speed.y *= -this.rebound_factor;
            this.ball.y = this.radius;
        }

        if (
            this.right_hand_pose != undefined &&
            this.right_hand_pose.length > 0
        ) {
            let left_bound = this.right_hand_pose.reduce(
                (a, b) => min(a, b[0]),
                width
            );
            let right_bound = this.right_hand_pose.reduce(
                (a, b) => max(a, b[0]),
                0
            );
            let top_bound = this.right_hand_pose.reduce(
                (a, b) => min(a, b[1]),
                height
            );
            let bottom_bound = this.right_hand_pose.reduce(
                (a, b) => max(a, b[1]),
                0
            );
            // console.log(left_bound, right_bound);
            if (
                this.ball.x > left_bound - this.radius &&
                this.ball.x < right_bound + this.radius &&
                this.ball.y > top_bound - this.radius &&
                this.ball.y < bottom_bound + this.radius &&
                !this.rebounded
                // this.speed.y > 0
            ) {
                let normal;
                if (this.right_hand_pose[12][0] > this.right_hand_pose[0][0]) {
                    normal = createVector(
                        -(
                            this.right_hand_pose[12][1] -
                            this.right_hand_pose[0][1]
                        ),
                        this.right_hand_pose[12][0] - this.right_hand_pose[0][0]
                    );
                } else {
                    normal = createVector(
                        this.right_hand_pose[12][1] -
                            this.right_hand_pose[0][1],
                        -(
                            this.right_hand_pose[12][0] -
                            this.right_hand_pose[0][0]
                        )
                    );
                }
                let projection =
                    p5.Vector.dot(this.speed, normal) /
                    p5.Vector.dot(normal, normal);
                this.speed = p5.Vector.add(
                    p5.Vector.mult(this.speed, -1),
                    p5.Vector.mult(normal, 2 * projection)
                );
                this.rebounded = true;
            }
        }

        if (
            this.left_hand_pose != undefined &&
            this.left_hand_pose.length > 0
        ) {
            let left_bound = this.left_hand_pose.reduce(
                (a, b) => min(a, b[0]),
                width
            );
            let right_bound = this.left_hand_pose.reduce(
                (a, b) => max(a, b[0]),
                0
            );
            let top_bound = this.left_hand_pose.reduce(
                (a, b) => min(a, b[1]),
                height
            );
            let bottom_bound = this.left_hand_pose.reduce(
                (a, b) => max(a, b[1]),
                0
            );
            // console.log(left_bound, right_bound);
            if (
                this.ball.x > left_bound - this.radius &&
                this.ball.x < right_bound + this.radius &&
                this.ball.y > top_bound - this.radius &&
                this.ball.y < bottom_bound + this.radius &&
                !this.rebounded
                // this.speed.y > 0
            ) {
                let normal;
                if (this.left_hand_pose[12][0] > this.left_hand_pose[0][0]) {
                    normal = createVector(
                        -(
                            this.left_hand_pose[12][1] -
                            this.left_hand_pose[0][1]
                        ),
                        this.left_hand_pose[12][0] - this.left_hand_pose[0][0]
                    );
                } else {
                    normal = createVector(
                        this.left_hand_pose[12][1] - this.left_hand_pose[0][1],
                        -(
                            this.left_hand_pose[12][0] -
                            this.left_hand_pose[0][0]
                        )
                    );
                }
                let projection =
                    p5.Vector.dot(this.speed, normal) /
                    p5.Vector.dot(normal, normal);
                this.speed = p5.Vector.add(
                    p5.Vector.mult(this.speed, -1),
                    p5.Vector.mult(normal, 2 * projection)
                );
                this.rebounded = true;
            }
        }
    }
}
