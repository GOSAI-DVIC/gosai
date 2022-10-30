/*
 * See https://github.com/osresearch/p5.projection for the math!
 *
 * Inspired by OpenCV perspectiveTransform()
 * https://docs.opencv.org/3.4/d2/de8/group__core__array.html#gad327659ac03e5fd6894b90025e6900a7
 */
class ProjectionMatrix
{
constructor(outPts=null, inPts=null, name=null)
{
	// default is a full HD canvas
	this.inPts = inPts ? inPts : [
		[   0,    0],
		[   0, 1080],
		[1920,    0],
		[1920, 1080],
	];

	// default is a slightly skewed rectangle
	this.outPts = outPts ? outPts : [
		[ -700, -400 ],
		[ -650, +300 ],
		[ 600, -150 ],
		[ 500, +450 ],
	];

	this.name = name;

	// no corner is currently moused and not dragging
	this.hit = -1;
	this.dragging = false;

	// do not start in edit mode
	this.edit = false;

	// pre-compute the forward and reverse projection matrices
	this.update();
}

save()
{
	if (this.name == null)
		return;
	storeItem(this.name, this.outPts);
}

/*
 * If a name is given, try to restore this one from a local storage.
 * This must be called in setup(), not before, since p5 hasn't initialized
 * everything yet.
 */
load()
{
	if (this.name == null)
		return;

	const stored = getItem(this.name);
	if (stored == null)
		return;

	console.log("Loaded " + this.name, stored);
	this.outPts = stored;
	this.update();
}



/*
 * After updating inPts or outPts, update() must be called
 * to recompute the inverse and forward projection matrices.
 * This is potentially expensive, so it should only be called
 * when necessary.
 */
update()
{
	this.mat = this.projectionMatrix(this.inPts, this.outPts);
	this.invmat = this.projectionMatrix(this.outPts, this.inPts);
}

projectionMatrix(inPts, outPts)
{
	const x0 = inPts[0][0];
	const x1 = inPts[1][0];
	const x2 = inPts[2][0];
	const x3 = inPts[3][0];

	const y0 = inPts[0][1];
	const y1 = inPts[1][1];
	const y2 = inPts[2][1];
	const y3 = inPts[3][1];

	const u0 = outPts[0][0];
	const u1 = outPts[1][0];
	const u2 = outPts[2][0];
	const u3 = outPts[3][0];

	const v0 = outPts[0][1];
	const v1 = outPts[1][1];
	const v2 = outPts[2][1];
	const v3 = outPts[3][1];

	const U = [
		[x0, y0, 1, 0, 0, 0, -x0*u0, -y0*u0],
		[x1, y1, 1, 0, 0, 0, -x1*u1, -y1*u1],
		[x2, y2, 1, 0, 0, 0, -x2*u2, -y2*u2],
		[x3, y3, 1, 0, 0, 0, -x3*u3, -y3*u3],
		[0, 0, 0, x0, y0, 1, -x0*v0, -y0*v0],
		[0, 0, 0, x1, y1, 1, -x1*v1, -y1*v1],
		[0, 0, 0, x2, y2, 1, -x2*v2, -y2*v2],
		[0, 0, 0, x3, y3, 1, -x3*v3, -y3*v3],
	];

	const b = [u0, u1, u2, u3, v0, v1, v2, v3];

	let m = math.lusolve(U, b).map((x) => x[0]);

	m.push(1); // c22 = 1

	return m;
}


drawCorner(sketch, n)
{
	let r = 20;
	sketch.fill(12,25,12);

	if (this.hit == n)
	{
		sketch.translate(0,0,1)
		sketch.fill(255,0,0);
		r *= 2;
	}

	sketch.rect(this.inPts[n][0]-r/2, this.inPts[n][1]-r/2, r, r);
}

drawBorder(sketch)
{
	sketch.push();

	// draw the border in a thick line
	sketch.strokeWeight(5);
	sketch.stroke(12,12,12);
	sketch.line(this.inPts[0][0], this.inPts[0][1], this.inPts[1][0], this.inPts[1][1]);
	sketch.line(this.inPts[1][0], this.inPts[1][1], this.inPts[3][0], this.inPts[3][1]);
	sketch.line(this.inPts[3][0], this.inPts[3][1], this.inPts[2][0], this.inPts[2][1]);
	sketch.line(this.inPts[2][0], this.inPts[2][1], this.inPts[0][0], this.inPts[0][1]);

	// draw the corners slightly larger and highlighted if the mouse
	// is over them.
	sketch.noStroke();
	this.drawCorner(sketch, 0);
	this.drawCorner(sketch, 1);
	this.drawCorner(sketch, 2);
	this.drawCorner(sketch, 3);

	sketch.pop();
}

drawMouse(sketch)
{
	// draw the mouse cross hairs in red and blue
	const uv = this.project(sketch.mouseX - sketch.width/2, sketch.mouseY - sketch.height/2);

	sketch.push();
	sketch.strokeWeight(1);
	sketch.noFill();

	sketch.stroke(0,0,255);
	sketch.line(-500, uv[1], 1920 + 500, uv[1]);
	// console.log(uv);

	sketch.stroke(255,0,0);
	sketch.line(uv[0], -500, uv[0], 1080 + 500);

	sketch.pop();
}

mouseMoved(sketch)
{
	const mx = sketch.mouseX - sketch.width/2;
	const my = sketch.mouseY - sketch.height/2;

	if (this.dragging)
	{
		if (!sketch.mouseIsPressed)
		{
			// end of drag
			this.dragging = false;
			return;
		}

		this.outPts[this.hit][0] = mx;
		this.outPts[this.hit][1] = my;

		// compute the forward and inverse projection matrices
		this.update();
		return;
	} else {
		// see if we hit any of our mouse
		// update the currently hit corner
		const r = 30;
		const r2 = r * r;

		this.hit = -1;

		for(let n = 0 ; n < 4 ; n++)
		{
			const dx = (this.outPts[n][0] - mx);
			const dy = (this.outPts[n][1] - my);
			const d2 = dx*dx + dy*dy;

			if (d2 < r2)
				this.hit = n;
		}

		// if they have pressed the mouse, then select the point
		if (sketch.mouseIsPressed && this.hit >= 0)
			this.dragging = true;
	}
}


/*
 * matrix is c00, c01, c02, c10, c11, c12, c20, c21, c22
 * ui = c00*xi + c01*yi + c02
 * vi = c10*xi + c11*yi + c12
 * zi = c20*xi + c21*yi + c22
 */
apply(sketch, debug=false)
{
	const mat = this.mat;

	sketch.applyMatrix(
		mat[0], mat[3], 0, mat[6],
		mat[1], mat[4], 0, mat[7],
		0,      0,      1, 0,
		mat[2], mat[5], 0, mat[8]
		);

	// if edit mode is enabled, handle mouse movement and border drawing
	if (this.edit)
	{
		this.mouseMoved(sketch);
		this.drawBorder(sketch);
	}

	if (debug >= 2){
		this.drawMouse(sketch);
	}

	// should check if mouse is inside the matrix
}

/*
 * convert screen coordinates to canvas coordinates
 * Remember that mouseX and mouseY are from the upper-left,
 * but the canvas is centered on the screen.
 */
project(x, y)
{
	const mat = this.invmat;
	const u = mat[0]*x + mat[1]*y + mat[2];
	const v = mat[3]*x + mat[4]*y + mat[5];
	const z = mat[6]*x + mat[7]*y + mat[8];

	return [ u/z, v/z ];
}
}
