


export function project2DPoint(point, matrix) {
    let [x, y] = point;
    let z = 1;
    let out = [];
    out[0] = x * matrix[0][0] + y * matrix[0][1] + z * matrix[0][2];
    out[1] = x * matrix[1][0] + y * matrix[1][1] + z * matrix[1][2];

    return out;
}


export function projectP5Context(context, matrix) {
    context.applyMatrix(matrix[0][0], matrix[1][0], matrix[0][1], matrix[1][1], matrix[0][2], matrix[1][2]);
    return context;
}
